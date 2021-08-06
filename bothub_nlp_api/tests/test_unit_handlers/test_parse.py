import unittest
from unittest.mock import patch
from celery.result import AsyncResult
from celery.exceptions import TimeLimitExceeded
from threading import Thread
from bothub_nlp_api.utils import ValidationError, AuthorizationIsRequired
from bothub_nlp_api.handlers.parse import check_language_priority, _parse
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException


class MockAsyncResult(AsyncResult):
    result = {"intents": [], "entities": []}

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
        self.repository_version = 299
        self.language = "pt_br"
        self.text = "parse test"

    def test_invalid_auth(self):
        with self.assertRaises(AuthorizationIsRequired):
            _parse("", "text", "pt_br", self.repository_version)
        with self.assertRaises(AuthorizationIsRequired):
            _parse(3, "text", "pt_br", self.repository_version)
        with self.assertRaises(AuthorizationIsRequired):
            _parse(None, "text", "pt_br", self.repository_version)

    def test_invalid_language(self):
        with self.assertRaises(ValidationError):
            _parse(
                self.authorization, "text", "invalid_language", self.repository_version
            )
        with self.assertRaises(ValidationError):
            _parse(self.authorization, "text", None, self.repository_version)
        with self.assertRaises(ValidationError):
            _parse(self.authorization, "text", 3, self.repository_version)

    def test_invalid_text(self):
        with self.assertRaises(ValidationError):
            _parse(self.authorization, "", self.language, self.repository_version)
        with self.assertRaises(ValidationError):
            _parse(self.authorization, None, self.language, self.repository_version)
        with self.assertRaises(ValidationError):
            _parse(self.authorization, 3, self.language, self.repository_version)

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse",
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": "pt_br",
            "algorithm": "transformer_network_diet_bert",
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    def test_check_language_priority_default(self, *args):
        check_language_priority(
            self.language, self.authorization, self.repository_version
        )

    @patch("bothub_nlp_api.handlers.parse.DEFAULT_LANGS_PRIORITY", {})
    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse",
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": "pt_br",
            "algorithm": "transformer_network_diet_bert",
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    def test_check_language_priority(self, *args):
        check_language_priority(
            self.language, self.authorization, self.repository_version
        )

    @patch(
        "bothub_backend.bothub.BothubBackend.request_backend_parse",
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": "pt_br",
            "algorithm": "transformer_network_diet_bert",
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    def test_validate_incorrect_region(self, *args):
        check_language_priority("pt_zz", self.authorization, self.repository_version)

    @patch("bothub_nlp_api.handlers.parse.check_language_priority", return_value={})
    def test_parse_invalid_language(self, *args):
        with self.assertRaises(ValidationError):
            _parse(self.authorization, "text", "pt_br", self.repository_version)

    @patch(
        "bothub_nlp_api.handlers.parse.check_language_priority",
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": "pt_br",
            "algorithm": "transformer_network_diet_bert",
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch(
        "bothub_nlp_api.handlers.parse.celery_app.send_task",
        return_value=MockAsyncResultTimeout(fake_id="0"),
    )
    def test_parse_mocked_celery_timeout(self, *args):
        with self.assertRaises(CeleryTimeoutException):
            _parse(self.authorization, "text", "pt_br", self.repository_version)

    @patch(
        "bothub_nlp_api.handlers.parse.check_language_priority",
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": "pt_br",
            "algorithm": "transformer_network_diet_bert",
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch(
        "bothub_nlp_api.handlers.parse.celery_app.send_task",
        return_value=MockAsyncResult(fake_id="0"),
    )
    @patch("bothub_nlp_api.handlers.parse.threading.Thread", return_value=MockThread())
    def test_parse_mocked_celery(self, *args):
        with self.assertRaises(AuthorizationIsRequired):
            _parse("", "text", "pt_br", self.repository_version)
        with self.assertRaises(ValidationError):
            _parse(self.authorization, "", "pt_br", self.repository_version)
        with self.assertRaises(ValidationError):
            _parse(self.authorization, None, "pt_br", self.repository_version)
        with self.assertRaises(ValidationError):
            _parse(self.authorization, 23, "pt_br", self.repository_version)

        _parse(self.authorization, "text", "pt_br", self.repository_version)
