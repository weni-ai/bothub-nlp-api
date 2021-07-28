from bothub_nlp_celery.actions import ACTION_WORD_SUGGESTION, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_WORD_SUGGESTION_TEXT

from bothub_nlp_api.utils import (
    ValidationError,
    language_validation
)


def _word_suggestion(text, language, n_words_to_generate):
    language_validation(language)

    if not text or type(text) != str:
        raise ValidationError("Invalid text")
    if (
        not n_words_to_generate
        or type(n_words_to_generate) != int
        or n_words_to_generate <= 0
        or n_words_to_generate > 50
    ):
        raise ValidationError("Invalid number of words to generate")

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
