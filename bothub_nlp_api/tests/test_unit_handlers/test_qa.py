import unittest
from unittest.mock import patch
from celery.result import AsyncResult
from celery.exceptions import TimeLimitExceeded
from threading import Thread
from bothub_nlp_api.utils import ValidationError, AuthorizationIsRequired
from bothub_nlp_api.handlers.question_answering import qa_handler
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException
from bothub_nlp_api.exceptions.question_answering_exceptions import (
    EmptyInputException,
    LargeContextException,
    LargeQuestionException,
)
from bothub_nlp_api.settings import (
    BOTHUB_NLP_API_QA_QUESTION_LIMIT,
    BOTHUB_NLP_API_QA_TEXT_LIMIT,
)


class MockAsyncResult(AsyncResult):
    result = {
        "answers": [
            {
                "text": "ans1",
                "confidence": "0.6759144631706974"
            },
            {
                "text": "ans2",
                "confidence": "0.3007182800642036"
            }
        ],
        "id": "0"
    }

    def __init__(self, fake_id):
        super().__init__(fake_id)

    def wait(self):
        pass


class MockAsyncResultTimeout(MockAsyncResult):
    def wait(self):
        raise TimeLimitExceeded


class MockThread(Thread):
    def __init__(self):
        super().__init__()

    def start(self):
        pass


class TestParseHandler(unittest.TestCase):
    def setUp(self):
        self.authorization = "Bearer aa11a1a1-111a-111a-11a1-aaa1a11aa111"
        self.knowledge_base_id = 1
        self.language = "en"
        self.question = "question example"

    def test_invalid_language(self):
        with self.assertRaises(ValidationError):
            qa_handler(
                self.authorization, self.knowledge_base_id, "question", "invalid_language"
            )
        with self.assertRaises(ValidationError):
            qa_handler(self.authorization, self.knowledge_base_id, "question", None)
        with self.assertRaises(ValidationError):
            qa_handler(self.authorization, self.knowledge_base_id, "question", 3)

    def test_invalid_auth(self):
        with self.assertRaises(AuthorizationIsRequired):
            qa_handler("", self.knowledge_base_id, "question", "en")
        with self.assertRaises(AuthorizationIsRequired):
            qa_handler(3, self.knowledge_base_id, "question", "en")
        with self.assertRaises(AuthorizationIsRequired):
            qa_handler(None, self.knowledge_base_id, "question", "en")

    def test_invalid_question(self):
        with self.assertRaises(EmptyInputException):
            qa_handler(self.authorization, self.knowledge_base_id, "", self.language)
        with self.assertRaises(EmptyInputException):
            qa_handler(self.authorization, self.knowledge_base_id, None, self.language)
        with self.assertRaises(EmptyInputException):
            qa_handler(self.authorization, self.knowledge_base_id, 3, self.language)

    def test_question_limit(self):
        with self.assertRaises(LargeQuestionException):
            qa_handler(
                self.authorization,
                self.knowledge_base_id,
                "a" * (BOTHUB_NLP_API_QA_QUESTION_LIMIT+1),
                self.language
            )

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_knowledge_bases",
        return_value={
            "text": "a" * (BOTHUB_NLP_API_QA_TEXT_LIMIT+1)
        },
    )
    def test_text_limit(self, *args):
        with self.assertRaises(LargeContextException):
            qa_handler(self.authorization, self.knowledge_base_id, self.question, self.language)

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_knowledge_bases",
        return_value={
            "text": ""
        },
    )
    def test_empty_text(self, *args):
        with self.assertRaises(EmptyInputException):
            qa_handler(self.authorization, self.knowledge_base_id, self.question, self.language)

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_knowledge_bases",
        return_value={
            "text": "text"
        },
    )
    @patch(
        "bothub_nlp_api.handlers.question_answering.celery_app.send_task",
        return_value=MockAsyncResultTimeout(fake_id="0"),
    )
    def test_qa_mocked_celery_timeout(self, *args):
        with self.assertRaises(CeleryTimeoutException):
            qa_handler(self.authorization, self.knowledge_base_id, "question", "pt_br")

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_knowledge_bases",
        return_value={
            "text": "text"
        },
    )
    @patch(
        "bothub_nlp_api.handlers.question_answering.celery_app.send_task",
        return_value=MockAsyncResult(fake_id="0"),
    )
    @patch("bothub_nlp_api.handlers.question_answering.threading.Thread", return_value=MockThread())
    def test_qa_mocked_celery(self, *args):
        with self.assertRaises(AuthorizationIsRequired):
            qa_handler("", self.knowledge_base_id, "question", "en")
        with self.assertRaises(EmptyInputException):
            qa_handler(self.authorization, self.knowledge_base_id, "", "en")
        with self.assertRaises(EmptyInputException):
            qa_handler(self.authorization, self.knowledge_base_id, None, "en")
        with self.assertRaises(EmptyInputException):
            qa_handler(self.authorization, self.knowledge_base_id, 23, "en")

        qa_handler(self.authorization, self.knowledge_base_id, "question", "en")
