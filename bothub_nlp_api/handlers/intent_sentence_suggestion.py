from bothub_nlp_celery.actions import ACTION_INTENT_SENTENCE_SUGGESTION, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_INTENT_SENTENCE_SUGGESTION_TEXT
from bothub_nlp_api.utils import get_repository_authorization
from bothub_nlp_api.utils import backend
from bothub_nlp_api import settings
from bothub_nlp_api.utils import ValidationError

import json


def _intent_sentence_suggestion(
    authorization, language, intent, n_sentences_to_generate, percentage_to_replace, repository_version=None,
):
    print(authorization)
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
    answer_task = celery_app.send_task(
        TASK_NLU_INTENT_SENTENCE_SUGGESTION_TEXT,
        args=[update.get("repository_version"), repository_authorization, intent, percentage_to_replace, n_sentences_to_generate],
        queue=queue_name(language, ACTION_INTENT_SENTENCE_SUGGESTION, 'SPACY'),
    )
    answer_task.wait()
    answer = answer_task.result
    answer.update(
        {
            "language": language,
            "n_sentences_to_generate": n_sentences_to_generate,
            "percentage_to_replace": percentage_to_replace,
            "intent": intent,
        }
    )
    return answer
