from bothub_nlp_celery.actions import ACTION_WORD_SUGGESTION, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_WORD_SUGGESTION_TEXT

from bothub_nlp_api import settings
from bothub_nlp_api.utils import ValidationError


def _word_suggestion(text, language, n_words_to_generate):
    from bothub_nlp_api.utils import DEFAULT_LANGS_PRIORITY

    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in DEFAULT_LANGS_PRIORITY.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    print(queue_name(language, ACTION_WORD_SUGGESTION, "SPACY"))
    answer_task = celery_app.send_task(
        TASK_NLU_WORD_SUGGESTION_TEXT,
        args=[text, n_words_to_generate],
        queue=queue_name(language, ACTION_WORD_SUGGESTION, "SPACY"),
    )
    answer_task.wait()
    answer = answer_task.result
    answer.update(
        {"text": text, "language": language, "n_words_to_generate": n_words_to_generate}
    )
    return answer
