from bothub_nlp_celery.actions import ACTION_WORDS_DISTIRBUTION, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_WORDS_DISTRIBUTION
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException
from celery.exceptions import TimeLimitExceeded

from bothub_nlp_api.utils import (
    backend,
    language_validation,
    repository_authorization_validation,
)


def _words_distribution(authorization, language, repository_version=None):
    language_validation(language)
    repository_authorization = repository_authorization_validation(authorization)

    current_update = backend().request_backend_train(
        repository_authorization, language, repository_version
    )

    try:
        answer_task = celery_app.send_task(
            TASK_NLU_WORDS_DISTRIBUTION,
            args=[
                current_update.get("current_version_id"),
                language,
                repository_authorization,
            ],
            queue=queue_name(language, ACTION_WORDS_DISTIRBUTION),
        )

        answer_task.wait()
        answer = answer_task.result
    except TimeLimitExceeded:
        raise CeleryTimeoutException()

    return answer
