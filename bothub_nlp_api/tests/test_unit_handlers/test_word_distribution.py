import unittest
from celery.result import AsyncResult
from unittest.mock import patch

from bothub_nlp_api.utils import ValidationError, AuthorizationIsRequired
from bothub_nlp_api.handlers.words_distribution import _words_distribution
from celery.exceptions import TimeLimitExceeded
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException


class MockAsyncResult(AsyncResult):
    result = {"id": 1, "version": 1}

    def __init__(self, fake_id):
        super().__init__(fake_id)

    def wait(self):
        pass


class MockAsyncResultTimeout(MockAsyncResult):
    def wait(self):
        raise TimeLimitExceeded


class TestWordsDistributionHandler(unittest.TestCase):
    def setUp(self):
        self.authorization = "Bearer aa11a1a1-111a-111a-11a1-aaa1a11aa111"
        self.language = "pt_br"

    def test_invalid_auth(self):
        with self.assertRaises(AuthorizationIsRequired):
            _words_distribution("", self.language)
        with self.assertRaises(AuthorizationIsRequired):
            _words_distribution(None, self.language)
        with self.assertRaises(AuthorizationIsRequired):
            _words_distribution(3, self.language)

    def test_invalid_language(self):
        with self.assertRaises(ValidationError):
            _words_distribution(self.authorization, "invalid_language")
        with self.assertRaises(ValidationError):
            _words_distribution(self.authorization, "")
        with self.assertRaises(ValidationError):
            _words_distribution(self.authorization, None)

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_train",
        return_value={
            "ready_for_train": True,
            "current_version_id": 1,
            "repository_authorization_user_id": 1,
            "language": "pt_br",
            "algorithm": "transformer_network_diet_bert",
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch(
        "bothub_nlp_api.handlers.words_distribution.celery_app.send_task",
        return_value=MockAsyncResultTimeout(fake_id="0"),
    )
    def test_celery_timeout(self, *args):
        with self.assertRaises(CeleryTimeoutException):
            _words_distribution(self.authorization, self.language)

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_train",
        return_value={
            "ready_for_train": True,
            "current_version_id": 1,
            "repository_authorization_user_id": 1,
            "language": "pt_br",
            "algorithm": "transformer_network_diet_bert",
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch(
        "bothub_nlp_api.handlers.words_distribution.celery_app.send_task",
        return_value=MockAsyncResult(fake_id="0"),
    )
    def test_default(self, *args):
        _words_distribution(self.authorization, self.language)
