import threading
import json

from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_QUESTION_ANSWERING
from bothub_nlp_celery.actions import ACTION_QUESTION_ANSWERING, queue_name
from bothub_nlp_api.exceptions.question_answering_exceptions import (
    LargeQuestionException,
    LargeContextException,
    EmptyInputException,
)
from bothub_nlp_api.utils import backend, repository_authorization_validation
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException
from celery.exceptions import TimeLimitExceeded


def qa_handler(
    authorization,
    knowledge_base_id,
    question,
    language,
    from_backend=False,
    user_agent=None,
):
    if len(question) > 500:
        raise LargeQuestionException(len(question))

    user_base_authorization = repository_authorization_validation(authorization)
    request = backend().request_backend_knowledge_bases(user_base_authorization, knowledge_base_id, language)
    text = request.get("text")

    if len(text) > 25000:
        raise LargeContextException(len(text))
    if len(text) == 0 or len(question) == 0:
        raise EmptyInputException()

    try:
        answer_task = celery_app.send_task(
            TASK_NLU_QUESTION_ANSWERING,
            args=[text, question, language],
            queue=queue_name(language, ACTION_QUESTION_ANSWERING, "QA"),
        )
        answer_task.wait()
        result = answer_task.result
    except TimeLimitExceeded:
        raise CeleryTimeoutException()

    answer = result["answers"][0]

    log = threading.Thread(
        target=backend().send_log_qa_nlp_parse,
        kwargs={
            "data": {
                "answer": answer["text"],
                "confidence": float(answer["confidence"]),
                "question": question,
                "user_agent": user_agent,
                "nlp_log": json.dumps(result),
                "user": str(user_base_authorization),
                "knowledge_base": int(knowledge_base_id),
                "language": language,
                "from_backend": from_backend,
            }
        },
    )
    log.start()

    return answer
