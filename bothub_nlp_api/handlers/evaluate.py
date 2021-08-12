from bothub_nlp_celery.actions import ACTION_EVALUATE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_EVALUATE_UPDATE
from celery.exceptions import TimeLimitExceeded
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException

from bothub_nlp_api import settings
from bothub_nlp_api.utils import (
    ValidationError,
    backend,
    send_job_train_ai_platform,
    get_language_model,
    language_validation,
    repository_authorization_validation,
)

import time

EVALUATE_STATUS_EVALUATED = "evaluated"
EVALUATE_STATUS_PROCESSING = "processing"
EVALUATE_STATUS_FAILED = "failed"


def crossvalidation_evaluate_handler(authorization, language, repository_version=None):
    repository_authorization = repository_authorization_validation(authorization)
    language_validation(language)

    try:
        repository = backend().request_backend_start_automatic_evaluate(
            repository_authorization, repository_version, language
        )
    except Exception:
        repository = {}

    if not repository.get("can_run_automatic_evaluate"):
        raise ValidationError("Validation error")

    model = get_language_model(repository)

    try:
        job_id = f'bothub_{settings.ENVIRONMENT}_evaluate_{repository.get("repository_version_language_id")}_{language}_{str(int(time.time()))}'
        send_job_train_ai_platform(
            jobId=job_id,
            repository_version=str(repository.get("repository_version_language_id")),
            by_id=str(repository.get("user_id")),
            repository_authorization=str(repository_authorization),
            language=language,
            type_model=model,
            operation="evaluate",
        )
        backend().request_backend_save_queue_id(
            update_id=str(repository.get("repository_version_language_id")),
            repository_authorization=str(repository_authorization),
            task_id=job_id,
            from_queue=0,
            type_processing=2,
        )
        evaluate_report = {
            "language": language,
            "status": EVALUATE_STATUS_PROCESSING,
            "repository_version": repository.get("repository_version_language_id"),
            "evaluate_id": None,
            "evaluate_version": None,
            "cross_validation": True,
        }
    except Exception as e:
        evaluate_report = {"status": EVALUATE_STATUS_FAILED, "error": str(e)}

    return evaluate_report


def evaluate_handler(authorization, language, repository_version=None):
    repository_authorization = repository_authorization_validation(authorization)
    language_validation(language)

    try:
        repository = backend().request_backend_evaluate(
            repository_authorization, language, repository_version
        )
    except Exception:
        repository = {}

    if not repository.get("update"):
        raise ValidationError("This repository has never been trained")

    model = get_language_model(repository)

    try:
        cross_validation = False
        evaluate_task = celery_app.send_task(
            TASK_NLU_EVALUATE_UPDATE,
            args=[
                repository_version,
                repository.get("repository_version"),  # repository_version_language_id
                repository_authorization,
                cross_validation,
                repository.get("language"),
            ],
            queue=queue_name(repository.get("language"), ACTION_EVALUATE, model),
        )
        evaluate_task.wait()
        evaluate = evaluate_task.result

        evaluate_report = {
            "language": language,
            "status": EVALUATE_STATUS_PROCESSING,
            "repository_version": repository.get("repository_version"),
            "evaluate_id": evaluate.get("id") if evaluate is not None else None,
            "evaluate_version": evaluate.get("version")
            if evaluate is not None
            else None,
            "cross_validation": cross_validation,
        }
    except TimeLimitExceeded:
        raise CeleryTimeoutException()
    except Exception as e:
        evaluate_report = {"status": EVALUATE_STATUS_FAILED, "error": str(e)}

    return evaluate_report
