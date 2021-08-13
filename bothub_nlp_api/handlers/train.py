import time
from bothub_nlp_celery.actions import ACTION_TRAIN, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE

from bothub_nlp_api import settings
from bothub_nlp_api.utils import backend, get_repository_authorization, get_language_model, send_job_train_ai_platform

TRAIN_STATUS_TRAINED = "trained"
TRAIN_STATUS_PROCESSING = "processing"
TRAIN_STATUS_FAILED = "failed"


def train_handler(authorization, repository_version=None, language=None):
    repository_authorization = get_repository_authorization(authorization)

    languages_report = {}
    train_tasks = []

    if language:
        language_status = backend().request_backend_train(
            repository_authorization, language, repository_version
        )
        ready_to_train_languages = [language_status] if language_status.get("ready_for_train") else []
    else:
        ready_to_train_languages = backend().request_all_readytotrain_languages(
            repository_authorization, repository_version
        )

    for update in ready_to_train_languages:

        model = get_language_model(update)
        if settings.BOTHUB_SERVICE_TRAIN == "celery":
            train_task = celery_app.send_task(
                TASK_NLU_TRAIN_UPDATE,
                args=[
                    update.get("current_version_id"),
                    update.get("repository_authorization_user_id"),
                    repository_authorization,
                ],
                queue=queue_name(update.get("language"), ACTION_TRAIN, model),
            )
            train_tasks.append({"task": train_task, "language": update.get("language")})
        elif settings.BOTHUB_SERVICE_TRAIN == "ai-platform":
            job_id = f'bothub_{settings.ENVIRONMENT}_train_{str(update.get("current_version_id"))}_{update.get("language")}_{str(int(time.time()))}'
            send_job_train_ai_platform(
                jobId=job_id,
                repository_version=str(update.get("current_version_id")),
                by_id=str(update.get("repository_authorization_user_id")),
                repository_authorization=str(repository_authorization),
                language=update.get("language"),
                type_model=model,
                operation="train",
            )
            backend().request_backend_save_queue_id(
                update_id=str(update.get("current_version_id")),
                repository_authorization=str(repository_authorization),
                task_id=job_id,
                from_queue=0,
                type_processing=0,
            )
        languages_report[update.get("language")] = {"status": TRAIN_STATUS_PROCESSING}

    resp = {
        "SUPPORTED_LANGUAGES": list(settings.SUPPORTED_LANGUAGES.keys()),
        "languages_report": languages_report,
    }
    return resp
