import unittest
from unittest.mock import patch
from celery.result import AsyncResult

from bothub_nlp_api.utils import ValidationError, AuthorizationIsRequired
from bothub_nlp_api.handlers.debug_parse import _debug_parse


class MockAsyncResult(AsyncResult):
    result = {
        'intents': [],
        'entities': []
    }

    def __init__(self, fake_id):
        super().__init__(fake_id)

    def wait(self):
        pass


class TestDebugParseHandler(unittest.TestCase):
    def setUp(self):
        self.authorization = 'Bearer da39f8a1-532a-459e-85c0-bfd8f96db828'
        self.repository_version = 299
        self.language = 'pt_br'
        self.text = "parse test"

    def test_invalid_language(self):
        with self.assertRaises(ValidationError):
            _debug_parse(self.authorization, self.text, 'invalid_language')
        with self.assertRaises(ValidationError):
            _debug_parse(self.authorization, self.text, None)
        with self.assertRaises(ValidationError):
            _debug_parse(self.authorization, self.text, '')

    def test_invalid_text(self):
        with self.assertRaises(ValidationError):
            _debug_parse(self.authorization, '', self.language)
        with self.assertRaises(ValidationError):
            _debug_parse(self.authorization, None, self.language)
        with self.assertRaises(ValidationError):
            _debug_parse(self.authorization, 2, self.language)

    def test_invalid_authorization(self):
        with self.assertRaises(AuthorizationIsRequired):
            _debug_parse('', self.text, self.language)
        with self.assertRaises(AuthorizationIsRequired):
            _debug_parse(None, self.text, self.language)
        with self.assertRaises(AuthorizationIsRequired):
            _debug_parse(2, self.text, self.language)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_parse',
        return_value={
            "version": False,
            "repository_version": 121212,
            "total_training_end": 0,
            "language": 'pt_br',
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    def test_no_version(self, *args):
        with self.assertRaises(ValidationError):
            _debug_parse(self.authorization, self.text, self.language)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_parse',
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": 'pt_br',
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch(
        'bothub_nlp_api.handlers.debug_parse.celery_app.send_task',
        return_value=MockAsyncResult(fake_id=0),
    )
    def test_default(self, *args):
        _debug_parse(self.authorization, self.text, self.language)
