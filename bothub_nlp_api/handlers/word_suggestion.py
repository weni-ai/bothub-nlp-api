from bothub_nlp_celery.actions import ACTION_WORD_SUGGESTION, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_WORD_SUGGESTION_TEXT

from bothub_nlp_api import settings
from bothub_nlp_api.utils import ValidationError


def _word_suggestion(
    text, language, n_words_to_generate
):
    from ..utils import NEXT_LANGS

    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in NEXT_LANGS.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    answer_task = celery_app.send_task(
        TASK_NLU_WORD_SUGGESTION_TEXT,
        args=[text, percentage_to_replace, n_sentences_to_generate, intent],
        queue=queue_name(ACTION_WORD_SUGGESTION, language, ALGORITHM_TO_LANGUAGE_MODEL[current_update.get("language")]),
    )
    answer_task.wait()
    answer = answer_task.result
    answer.update(
        {
            "text": text,
            "language": language,
            "n_words_to_generate": n_words_to_generate,
        }
    )
    return answer
