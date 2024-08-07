import time
import threading
import bothub_backend
import google.oauth2.credentials
import bothub_nlp_celery.settings as celery_settings
import json
import logging
import requests

from fastapi import HTTPException, Header
from googleapiclient import discovery
from googleapiclient import errors
from starlette.requests import Request
from bothub_nlp_api import settings


def backend():
    return bothub_backend.get_backend(
        "bothub_backend.bothub.BothubBackend", settings.BOTHUB_ENGINE_URL
    )


DEFAULT_LANGS_PRIORITY = {
    "english": ["en"],
    "portuguese": ["pt_br", "pt"],
    "pt": ["pt_br", "pt"],
    "pt-br": ["pt_br"],
    "br": ["pt_br"],
}

ALGORITHM_TO_LANGUAGE_MODEL = {
    "neural_network_internal": None,
    "neural_network_external": "SPACY",
    "transformer_network_diet": None,
    "transformer_network_diet_word_embedding": "SPACY",
    "transformer_network_diet_bert": "BERT",
}


class AuthorizationIsRequired(HTTPException):
    def __init__(self):
        self.status_code = 401
        self.detail = "Authorization is required"


class ValidationError(HTTPException):
    def __init__(self, message):
        self.status_code = 400
        self.detail = message


def repository_authorization_validation(authorization_header_value):
    if type(authorization_header_value) != str:
        raise AuthorizationIsRequired()

    authorization_uuid = authorization_header_value and authorization_header_value[7:]

    if not authorization_uuid:
        raise AuthorizationIsRequired()

    return authorization_uuid


class AuthorizationRequired:
    async def __call__(
        self,
        request: Request,
        Authorization: str = Header(..., description="Bearer your_key"),
    ):
        if request.method == "OPTIONS":
            return True

        repository_authorization_validation(Authorization)
        return True


def language_validation(language):
    if not language or (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in DEFAULT_LANGS_PRIORITY.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    return


def wenigpt_language_validation(language: str):
    valid_languages = settings.WENIGPT_SUPPORTED_LANGUAGES.split("|")
    if language and language.lower() in valid_languages:
        return
    raise ValidationError(f"Language '{language}' not supported by now.")


def get_train_job_status(job_name):
    jobId = f"projects/{settings.BOTHUB_GOOGLE_PROJECT_ID}/jobs/{job_name}"

    credentials = google.oauth2.credentials.Credentials(
        "access_token",
        refresh_token=settings.BOTHUB_GOOGLE_CREDENTIALS_REFRESH_TOKEN,
        token_uri=settings.BOTHUB_GOOGLE_CREDENTIALS_TOKEN_URI,
        client_id=settings.BOTHUB_GOOGLE_CREDENTIALS_CLIENT_ID,
        client_secret=settings.BOTHUB_GOOGLE_CREDENTIALS_CLIENT_SECRET,
    )

    # Consiga uma representação em Python dos serviços do AI Platform Training:
    cloudml = discovery.build(
        "ml", "v1", credentials=credentials, cache_discovery=False
    )

    request = cloudml.projects().jobs().get(name=jobId)

    try:
        response = request.execute()
    except errors.HttpError as e:
        raise e

    if response is None:
        raise HTTPException(status_code=401, detail="Got None as response.")

    return response


def cancel_job_after_time(t, cloudml, job_name):
    time.sleep(t)

    request = cloudml.projects().jobs().cancel(name=job_name)

    try:
        request.execute()
        logging.debug(f"Canceling job {job_name} due timeout.")
    except errors.HttpError:
        pass
    except Exception as err:
        logging.debug(err)
        raise Exception(f"Something went wrong with job {job_name}: {err}")


def send_job_train_ai_platform(
    jobId,
    repository_version,
    by_id,
    repository_authorization,
    language,
    type_model,
    operation="train",
):
    if (
        type_model == "BERT" and
        (language == "xx" or language not in celery_settings.AVAILABLE_BERT_MODELS)
    ):
        image_sufix = "-xx-BERT"
    elif type_model is not None:
        image_sufix = f"-{language}-{type_model}"
    else:
        image_sufix = "-xx-NONE"

    args = [
        "--operation",
        operation,
        "--repository-version",
        repository_version,
        "--by-id",
        by_id,
        "--repository-authorization",
        repository_authorization,
        "--base_url",
        settings.BOTHUB_ENGINE_URL,
        "--AIPLATFORM_LANGUAGE_QUEUE",
        language,
    ]

    if type_model is not None:
        args.extend(["--AIPLATFORM_LANGUAGE_MODEL", type_model])

    if operation == "evaluate":
        args.extend(
            [
                "--BOTHUB_NLP_AWS_S3_BUCKET_NAME",
                settings.BOTHUB_NLP_AWS_S3_BUCKET_NAME,
                "--BOTHUB_NLP_AWS_ACCESS_KEY_ID",
                settings.BOTHUB_NLP_AWS_ACCESS_KEY_ID,
                "--BOTHUB_NLP_AWS_SECRET_ACCESS_KEY",
                settings.BOTHUB_NLP_AWS_SECRET_ACCESS_KEY,
                "--BOTHUB_NLP_AWS_REGION_NAME",
                settings.BOTHUB_NLP_AWS_REGION_NAME,
            ]
        )

    training_inputs = {
        "scaleTier": "CUSTOM",
        "masterType": "standard_p100",
        "masterConfig": {
            "imageUri": f"{settings.BOTHUB_GOOGLE_AI_PLATFORM_REGISTRY}:"
            f"{settings.BOTHUB_GOOGLE_AI_PLATFORM_IMAGE_VERSION}{image_sufix}"
        },
        "packageUris": settings.BOTHUB_GOOGLE_AI_PLATFORM_PACKAGE_URI,
        "pythonModule": "trainer.train",
        "args": args,
        "region": "us-east1",
        "jobDir": "gs://poc-training-ai-platform/job-dir",
    }

    job_spec = {"jobId": jobId, "trainingInput": training_inputs}

    project_id = f"projects/{settings.BOTHUB_GOOGLE_PROJECT_ID}"

    credentials = google.oauth2.credentials.Credentials(
        "access_token",
        refresh_token=settings.BOTHUB_GOOGLE_CREDENTIALS_REFRESH_TOKEN,
        token_uri=settings.BOTHUB_GOOGLE_CREDENTIALS_TOKEN_URI,
        client_id=settings.BOTHUB_GOOGLE_CREDENTIALS_CLIENT_ID,
        client_secret=settings.BOTHUB_GOOGLE_CREDENTIALS_CLIENT_SECRET,
    )

    # Consiga uma representação em Python dos serviços do AI Platform Training:
    cloudml = discovery.build(
        "ml", "v1", credentials=credentials, cache_discovery=False
    )

    # Crie e envie sua solicitação:
    request = cloudml.projects().jobs().create(body=job_spec, parent=project_id)

    try:
        # Envia job de treinamento
        request.execute()

        # Envia requisição de cancelamento depois de <settings.BOTHUB_GOOGLE_AI_PLATFORM_JOB_TIMEOUT> segundos
        # para jobs que travaram e continuam rodando
        if settings.BOTHUB_GOOGLE_AI_PLATFORM_JOB_TIMEOUT is not None:
            time_seconds = int(settings.BOTHUB_GOOGLE_AI_PLATFORM_JOB_TIMEOUT)
            if operation == "evaluate":
                time_seconds = time_seconds * 2

            threading.Thread(
                target=cancel_job_after_time,
                args=(time_seconds, cloudml, f"{project_id}/jobs/{jobId}"),
            ).start()
    except errors.HttpError as err:
        raise HTTPException(
            status_code=401,
            detail=f"There was an error creating the training job. Check the details: {err}",
        )


def get_language_model(update):
    model = ALGORITHM_TO_LANGUAGE_MODEL[update.get("algorithm")]
    language = update.get("language")

    if model == "SPACY" and language not in celery_settings.AVAILABLE_SPACY_MODELS:
        model = None

    # Send parse to SPACY worker to use name_entities (only if BERT not in use)
    if (
        (update.get("use_name_entities"))
        and (model is None)
        and (language in celery_settings.AVAILABLE_SPACY_MODELS)
    ):
        model = "SPACY"

    return model

language_to_qa_model = {
    'en': 'en',
    'pt_br': 'pt_br',
    'pt': 'pt_br',
}


def request_wenigpt(context, question):

    url = settings.WENIGPT_API_URL
    token = settings.WENIGPT_API_TOKEN
    cookie = settings.WENIGPT_COOKIE
    base_prompt = f"{settings.WENIGPT_PROMPT_INTRODUCTION}{settings.WENIGPT_PROMPT_TEXT}{context}{settings.WENIGPT_PROMPT_QUESTION}{question}{settings.WENIGPT_PROMPT_REINFORCEMENT_INSTRUCTION}{settings.WENIGPT_PROMPT_ANSWER}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Cookie": cookie
    }
    data = {
        "input": {
            "prompt": base_prompt,
            "sampling_params": {
                "max_new_tokens": settings.WENIGPT_MAX_NEW_TOKENS,
                "max_length": settings.WENIGPT_MAX_LENGHT,
                "top_p": settings.WENIGPT_TOP_P,
                "top_k": settings.WENIGPT_TOP_K,
                "temperature": settings.WENIGPT_TEMPERATURE,
                "do_sample": False,
                "stop": settings.WENIGPT_STOP,
            }
        }
    }

    text_answers = None

    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(data))
        print(f"[ WENIGPT REQUEST] - {response.text}")
        response_json = response.json()
        text_answers = response_json["output"].get("text")
    except Exception as e:
        response = {"error": str(e)}
        print(f"[ WENIGPT REQUEST ] {response}")

    answers = []
    if text_answers:
        for answer in text_answers:
            answer = answer.strip()
            ans = ""
            for ch in answer:
                if ch == '\n':
                    break
                ans += ch
            answers.append({"text": ans})
    return {"answers": answers, "id": "0"}
