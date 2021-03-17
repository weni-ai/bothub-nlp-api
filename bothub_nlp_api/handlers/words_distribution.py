from bothub_nlp_api import settings
from bothub_nlp_celery.actions import ACTION_WORDS_DISTIRBUTION, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_WORDS_DISTRIBUTION
from bothub_nlp_api.utils import get_repository_authorization
from bothub_nlp_api.utils import ValidationError
from bothub_nlp_api.utils import backend


def _words_distribution(authorization, language, repository_version=None):
    from bothub_nlp_api.utils import DEFAULT_LANGS_PRIORITY

    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in DEFAULT_LANGS_PRIORITY.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    repository_authorization = get_repository_authorization(authorization)

    current_update = backend().request_backend_train(
        repository_authorization, language, repository_version
    )

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
    return answer
