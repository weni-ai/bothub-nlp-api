import threading
import json

from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_QUESTION_ANSWERING
from bothub_nlp_celery.actions import ACTION_QUESTION_ANSWERING, queue_name
from bothub_nlp_api.exceptions.question_answering_exceptions import (
    LargeQuestionException,
    LargeContextException,
    EmptyInputException,
    EmptyBaseException,
)
from bothub_nlp_api.utils import backend, repository_authorization_validation, language_validation
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException
from celery.exceptions import TimeLimitExceeded
from bothub_nlp_api.settings import BOTHUB_NLP_API_QA_TEXT_LIMIT, BOTHUB_NLP_API_QA_QUESTION_LIMIT


def qa_handler(
    authorization,
    knowledge_base_id,
    question,
    language,
    from_backend=False,
    user_agent=None,
):
    language_validation(language)
    user_base_authorization = repository_authorization_validation(authorization)

    if not question or type(question) != str:
        raise EmptyInputException()
    elif len(question) > BOTHUB_NLP_API_QA_QUESTION_LIMIT:
        raise LargeQuestionException(len(question), limit=BOTHUB_NLP_API_QA_QUESTION_LIMIT)

    request = backend().request_backend_knowledge_bases(user_base_authorization, knowledge_base_id, language)
    text = request.get("text")

    if not text:
        raise EmptyBaseException()
    elif len(text) > BOTHUB_NLP_API_QA_TEXT_LIMIT:
        raise LargeContextException(len(text), limit=BOTHUB_NLP_API_QA_TEXT_LIMIT)

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

    return result
