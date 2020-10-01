from bothub_nlp_celery.actions import ACTION_DEBUG_PARSE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_DEBUG_PARSE_TEXT
from bothub_nlp_celery.utils import ALGORITHM_TO_LANGUAGE_MODEL
from bothub_nlp_celery import settings as celery_settings

from bothub_nlp_api import settings
from bothub_nlp_api.utils import AuthorizationIsRequired
from bothub_nlp_api.utils import ValidationError
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import get_repository_authorization


def _debug_parse(authorization, text, language, repository_version=None):
    from ..utils import DEFAULT_LANGS_PRIORITY

    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in DEFAULT_LANGS_PRIORITY.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    repository_authorization = get_repository_authorization(authorization)
    if not repository_authorization:
        raise AuthorizationIsRequired()

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

    chosen_algorithm = update.get("algorithm")
    # chosen_algorithm = choose_best_algorithm(update.get("language"))
    model = ALGORITHM_TO_LANGUAGE_MODEL[chosen_algorithm]

    if (model == "SPACY" and language not in celery_settings.SPACY_LANGUAGES) or (
        model == "BERT" and language not in celery_settings.BERT_LANGUAGES
    ):
        model = None
    if not update.get("version"):
        raise ValidationError("This repository has never been trained")

    answer_task = celery_app.send_task(
        TASK_NLU_DEBUG_PARSE_TEXT,
        args=[update.get("repository_version"), repository_authorization, text],
        queue=queue_name(update.get("language"), ACTION_DEBUG_PARSE, model),
    )
    answer_task.wait()
    answer = answer_task.result
    answer.update(
        {
            "text": text,
            "repository_version": update.get("repository_version"),
            "language": update.get("language"),
        }
    )
    return answer
