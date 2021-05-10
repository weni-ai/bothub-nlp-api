import time
import threading
import bothub_backend
import google.oauth2.credentials
import bothub_nlp_api.settings
import bothub_nlp_celery.settings as celery_settings
import logging

from fastapi import HTTPException, Header
from googleapiclient import discovery
from googleapiclient import errors
from starlette.requests import Request
from bothub_nlp_api import settings


def backend():
    return bothub_backend.get_backend(
        "bothub_backend.bothub.BothubBackend", bothub_nlp_api.settings.BOTHUB_ENGINE_URL
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


def get_repository_authorization(authorization_header_value):
    authorization_uuid = authorization_header_value and authorization_header_value[7:]

    if not authorization_uuid:
        return False

    return authorization_uuid


class AuthorizationRequired:
    async def __call__(
        self,
        request: Request,
        Authorization: str = Header(..., description="Bearer your_key"),
    ):
        if request.method == "OPTIONS":
            return True

        repository_authorization = get_repository_authorization(Authorization)
        if not repository_authorization:
            raise HTTPException(status_code=401, detail="Authorization is required")
        return True


def language_validation(language):
    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in DEFAULT_LANGS_PRIORITY.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    return


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
        raise Exception(f'Something went wrong with job {job_name}: {err}')


def send_job_train_ai_platform(
    jobId,
    repository_version,
    by_id,
    repository_authorization,
    language,
    type_model,
    operation="train",
):
    if type_model == 'BERT' and language not in celery_settings.BERT_LANGUAGES:
        image_sufix = "-xx-BERT"
    elif type_model is not None:
        image_sufix = f"-{language}-{type_model}"
    else:
        image_sufix = "-xx-SPACY"

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
        bothub_nlp_api.settings.BOTHUB_ENGINE_URL,
        "--AIPLATFORM_LANGUAGE_QUEUE",
        language,
    ]

    if type_model is not None:
        args.extend(["--AIPLATFORM_LANGUAGE_MODEL", type_model])

    if operation == "evaluate":
        args.extend(
            [
                "--BOTHUB_NLP_AWS_S3_BUCKET_NAME", settings.BOTHUB_NLP_AWS_S3_BUCKET_NAME,
                "--BOTHUB_NLP_AWS_ACCESS_KEY_ID", settings.BOTHUB_NLP_AWS_ACCESS_KEY_ID,
                "--BOTHUB_NLP_AWS_SECRET_ACCESS_KEY", settings.BOTHUB_NLP_AWS_SECRET_ACCESS_KEY,
                "--BOTHUB_NLP_AWS_REGION_NAME", settings.BOTHUB_NLP_AWS_REGION_NAME,
            ]
        )

    training_inputs = {
        "scaleTier": "CUSTOM",
        "masterType": "standard_gpu",
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
            if operation == 'evaluate':
                time_seconds = time_seconds * 2

            threading.Thread(
                target=cancel_job_after_time,
                args=(
                    time_seconds,
                    cloudml,
                    f"{project_id}/jobs/{jobId}",
                )
            ).start()
    except errors.HttpError as err:
        raise HTTPException(
            status_code=401,
            detail=f"There was an error creating the training job. Check the details: {err}",
        )


def get_language_model(update):
    model = ALGORITHM_TO_LANGUAGE_MODEL[update.get("algorithm")]
    language = update.get("language")

    if model == "SPACY" and language not in celery_settings.SPACY_LANGUAGES:
        model = None

    # Send parse to SPACY worker to use name_entities (only if BERT not in use)
    if (
        (update.get("use_name_entities"))
        and (model is None)
        and (language in celery_settings.SPACY_LANGUAGES)
    ):
        model = "SPACY"

    return model
