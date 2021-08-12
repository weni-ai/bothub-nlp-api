from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_QUESTION_ANSWERING
from bothub_nlp_api.exceptions.question_answering_exceptions import (
    LargeQuestionException,
    LargeContextException,
    EmptyInputException,
)
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException
from celery.exceptions import TimeLimitExceeded


def qa_handler(context, question, language):

    if len(context) > 25000:
        raise LargeContextException(len(context))
    if len(question) > 500:
        raise LargeQuestionException(len(question))
    if len(context) == 0 or len(question) == 0:
        raise EmptyInputException()

    try:
        answer_task = celery_app.send_task(
            TASK_NLU_QUESTION_ANSWERING, args=[context, question, language], queue="QA"
        )
        answer_task.wait()
        answer = answer_task.result
    except TimeLimitExceeded:
        raise CeleryTimeoutException()

    return answer
