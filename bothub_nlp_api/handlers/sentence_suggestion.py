from bothub_nlp_celery.actions import ACTION_SENTENCE_SUGGESTION, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_SENTENCE_SUGGESTION_TEXT

from bothub_nlp_api.utils import (
    language_validation,
    ValidationError
)
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException
from celery.exceptions import TimeLimitExceeded


def _sentence_suggestion(
    text, language, n_sentences_to_generate, percentage_to_replace
):
    language_validation(language)

    if not text or type(text) != str:
        raise ValidationError("Invalid text")
    if (
        not n_sentences_to_generate
        or type(n_sentences_to_generate) != int
        or n_sentences_to_generate <= 0
        or n_sentences_to_generate > 50
    ):
        raise ValidationError("Invalid number of sentences to generate")
    if (
        not percentage_to_replace
        or type(percentage_to_replace) != int
        or percentage_to_replace <= 0
        or percentage_to_replace > 100
    ):
        raise ValidationError("Invalid percentage to replace")

    try:
        answer_task = celery_app.send_task(
            TASK_NLU_SENTENCE_SUGGESTION_TEXT,
            args=[text, percentage_to_replace, n_sentences_to_generate],
            queue=queue_name(language, ACTION_SENTENCE_SUGGESTION, "SPACY"),
        )
        answer_task.wait()
        answer = answer_task.result
    except TimeLimitExceeded:
        raise CeleryTimeoutException()

    answer.update(
        {
            "text": text,
            "language": language,
            "n_sentences_to_generate": n_sentences_to_generate,
            "percentage_to_replace": percentage_to_replace,
        }
    )
    return answer
