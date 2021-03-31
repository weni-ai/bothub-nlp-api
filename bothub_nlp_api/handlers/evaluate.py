from bothub_nlp_celery.actions import ACTION_EVALUATE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_EVALUATE_UPDATE

from bothub_nlp_api import settings
from bothub_nlp_api.utils import AuthorizationIsRequired
from bothub_nlp_api.utils import DEFAULT_LANGS_PRIORITY
from bothub_nlp_api.utils import ValidationError, get_repository_authorization
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import send_job_train_ai_platform
from bothub_nlp_api.utils import get_language_model
import time

EVALUATE_STATUS_EVALUATED = "evaluated"
EVALUATE_STATUS_PROCESSING = "processing"
EVALUATE_STATUS_FAILED = "failed"


def crossvalidation_evaluate_handler(
    authorization, language, repository_version=None
):
    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in DEFAULT_LANGS_PRIORITY.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    repository_authorization = get_repository_authorization(authorization)
    if not repository_authorization:
        raise AuthorizationIsRequired()

    try:
        update = backend().request_backend_start_automatic_evaluate(
            repository_authorization, repository_version, language
        )
    except Exception as err:
        print(err)
        update = {}

    if not update.get("can_run_automatic_evaluate"):
        raise ValidationError("Validation error")

    model = get_language_model(update)

    try:
        job_id = f'bothub_{settings.ENVIRONMENT}_evaluate_{update.get("repository_version_language_id")}_{language}_{str(int(time.time()))}'
        send_job_train_ai_platform(
            jobId=job_id,
            repository_version=str(update.get("repository_version_language_id")),
            by_id=str(update.get("user_id")),
            repository_authorization=str(repository_authorization),
            language=language,
            type_model=model,
            operation="evaluate",
        )
        backend().request_backend_save_queue_id(
            update_id=str(update.get("repository_version_language_id")),
            repository_authorization=str(repository_authorization),
            task_id=job_id,
            from_queue=0,
            type_processing=2,
        )
        evaluate_report = {
            "language": language,
            "status": EVALUATE_STATUS_PROCESSING,
            "repository_version": update.get("repository_version_language_id"),
            "evaluate_id": None,
            "evaluate_version": None,
            "cross_validation": True,
        }
    except Exception as e:
        evaluate_report = {"status": EVALUATE_STATUS_FAILED, "error": str(e)}

    return evaluate_report


def evaluate_handler(
    authorization, language, repository_version=None
):
    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in DEFAULT_LANGS_PRIORITY.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    repository_authorization = get_repository_authorization(authorization)
    if not repository_authorization:
        raise AuthorizationIsRequired()

    try:
        update = backend().request_backend_evaluate(
            repository_authorization, language, repository_version
        )
    except Exception:
        update = {}

    if not update.get("update"):
        raise ValidationError("This repository has never been trained")

    model = get_language_model(update)

    try:
        evaluate = None
        cross_validation = False
        evaluate_task = celery_app.send_task(
            TASK_NLU_EVALUATE_UPDATE,
            args=[
                update.get("repository_version"),
                repository_authorization,
                cross_validation,
                update.get("language")
            ],
            queue=queue_name(update.get("language"), ACTION_EVALUATE, model),
        )
        evaluate_task.wait()
        evaluate = evaluate_task.result

        evaluate_report = {
            "language": language,
            "status": EVALUATE_STATUS_PROCESSING,
            "repository_version": update.get("repository_version"),
            "evaluate_id": evaluate.get("id") if evaluate is not None else None,
            "evaluate_version": evaluate.get("version")
            if evaluate is not None
            else None,
            "cross_validation": cross_validation,
        }
    except Exception as e:
        evaluate_report = {"status": EVALUATE_STATUS_FAILED, "error": str(e)}

    return evaluate_report
