from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_QUESTION_ANSWERING
from bothub_nlp_api.utils import AuthorizationIsRequired
from bothub_nlp_api.utils import get_repository_authorization
from bothub_nlp_api.exceptions.question_answering_exceptions import (
    LargeQuestionException,
    EmptyInputException
)


def qa_handler(knowledge_base_id, question, language, authorization):

    repository_authorization = get_repository_authorization(authorization)
    if not repository_authorization:
        raise AuthorizationIsRequired()

    if len(question) > 500:
        raise LargeQuestionException(len(question))
    if len(question) == 0:
        raise EmptyInputException()

    answer_task = celery_app.send_task(
        TASK_NLU_QUESTION_ANSWERING,
        args=[
            knowledge_base_id,
            question,
            language,
            repository_authorization
        ],
        queue="QA",
    )
    answer_task.wait()
    answer = answer_task.result

    return answer
