from bothub_nlp_celery.actions import ACTION_DEBUG_PARSE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_DEBUG_PARSE_TEXT
from celery.exceptions import TimeLimitExceeded
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException


from bothub_nlp_api.utils import (
    ValidationError,
    backend,
    get_language_model,
    language_validation,
    repository_authorization_validation,
)


def _debug_parse(authorization, text, language, repository_version=None):
    from ..utils import DEFAULT_LANGS_PRIORITY

    language_validation(language)
    repository_authorization = repository_authorization_validation(authorization)

    if type(text) != str or not text:
        raise ValidationError("Text required.")

    try:
        update = backend().request_backend_parse(
            repository_authorization, language, repository_version
        )
    except Exception:
        update = {}

    if not update.get("version"):
        next_languages = DEFAULT_LANGS_PRIORITY.get(language, [])
        for next_language in next_languages:
            update = backend().request_backend_parse(
                repository_authorization, next_language, repository_version
            )
            if update.get("version"):
                break

    if not update.get("version"):
        raise ValidationError("This repository has never been trained")

    model = get_language_model(update)
    try:
        answer_task = celery_app.send_task(
            TASK_NLU_DEBUG_PARSE_TEXT,
            args=[update.get("repository_version"), repository_authorization, text],
            queue=queue_name(update.get("language"), ACTION_DEBUG_PARSE, model),
        )
        answer_task.wait()
        answer = answer_task.result
    except TimeLimitExceeded:
        raise CeleryTimeoutException()

    answer.update(
        {
            "text": text,
            "repository_version": update.get("repository_version"),
            "language": update.get("language"),
        }
    )
    return answer
