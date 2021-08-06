from bothub_nlp_celery.actions import ACTION_INTENT_SENTENCE_SUGGESTION, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_INTENT_SENTENCE_SUGGESTION_TEXT
from celery.exceptions import TimeLimitExceeded
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException

from bothub_nlp_api.utils import (
    ValidationError,
    backend,
    language_validation,
    repository_authorization_validation
)


def _intent_sentence_suggestion(
    authorization,
    language,
    intent,
    n_sentences_to_generate,
    percentage_to_replace,
    repository_version=None,
):
    repository_authorization = repository_authorization_validation(authorization)
    language_validation(language)

    if not intent or type(intent) != str:
        raise ValidationError("Invalid intent")
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
        update = backend().request_backend_parse(
            repository_authorization, language, repository_version
        )
    except Exception:
        update = {}
    try:
        answer_task = celery_app.send_task(
            TASK_NLU_INTENT_SENTENCE_SUGGESTION_TEXT,
            args=[
                update.get("repository_version"),
                repository_authorization,
                intent,
                percentage_to_replace,
                n_sentences_to_generate,
            ],
            queue=queue_name(language, ACTION_INTENT_SENTENCE_SUGGESTION, "SPACY"),
        )
        answer_task.wait()
        answer = answer_task.result
    except TimeLimitExceeded:
        raise CeleryTimeoutException()

    answer.update(
        {
            "language": language,
            "n_sentences_to_generate": n_sentences_to_generate,
            "percentage_to_replace": percentage_to_replace,
            "intent": intent,
        }
    )
    return answer
