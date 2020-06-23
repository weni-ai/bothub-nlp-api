import json
from urllib.parse import urlencode
from urllib.request import urlopen

import bothub_backend
import requests

import bothub_nlp_api.settings
from fastapi import HTTPException, Header
from starlette.requests import Request
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient import errors
import google.oauth2.credentials

from bothub_nlp_api import settings


def backend():
    return bothub_backend.get_backend(
        "bothub_backend.bothub.BothubBackend", bothub_nlp_api.settings.BOTHUB_ENGINE_URL
    )


NEXT_LANGS = {
    "english": ["en"],
    "portuguese": ["pt", "pt_br"],
    "pt": ["pt_br"],
    "pt-br": ["pt_br"],
    "br": ["pt_br"],
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

    if response == None:
        raise Exception("Got None as response.")

    return response


def send_job_train_ai_platform(
    jobId, repository_version, by_id, repository_authorization
):
    training_inputs = {
        "scaleTier": "CUSTOM",
        "masterType": "standard_p100",
        "masterConfig": {
            "imageUri": "us.gcr.io/bothub-273521/bothub-nlp-ai-platform:1.0.37"
        },
        "packageUris": [
            "gs://poc-training-ai-platform/bothub-nlp-ai-platform/bothub-nlp-ai-platform-0.1.tar.gz"
        ],
        "pythonModule": "trainer.train",
        "args": [
            "--repository-version",
            repository_version,
            "--by-id",
            by_id,
            "--repository-authorization",
            repository_authorization,
            "--base_url",
            bothub_nlp_api.settings.BOTHUB_ENGINE_URL
        ],
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
        request.execute()
        return True

    except errors.HttpError as err:
        # Do whatever error response is appropriate for your application.
        # For this example, just send some text to the logs.
        # You need to import logging for this to work.
        print("There was an error creating the training job. Check the details:")
        print(err)
    return False
