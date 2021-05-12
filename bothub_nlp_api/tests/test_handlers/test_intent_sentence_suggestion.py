import unittest
from celery.result import AsyncResult
from unittest.mock import patch

from bothub_nlp_api.utils import ValidationError, AuthorizationIsRequired
from bothub_nlp_api.handlers.intent_sentence_suggestion import _intent_sentence_suggestion


class MockAsyncResult(AsyncResult):
    result = {
        'id': 1,
        'version': 1,
    }

    def __init__(self, fake_id):
        super().__init__(fake_id)

    def wait(self):
        pass


class TestIntentSentenceSuggestionHandler(unittest.TestCase):
    def setUp(self):
        self.authorization = 'Bearer da39f8a1-532a-459e-85c0-bfd8f96db828'
        self.repository_version = 299
        self.language = 'pt_br'
        self.intent = 'test'

    def test_invalid_auth(self):
        with self.assertRaises(AuthorizationIsRequired):
            _intent_sentence_suggestion('', self.language, self.intent, 5, 60)
        with self.assertRaises(AuthorizationIsRequired):
            _intent_sentence_suggestion(None, self.language, self.intent, 5, 60)
        with self.assertRaises(AuthorizationIsRequired):
            _intent_sentence_suggestion(2, self.language, self.intent, 5, 60)

    def test_invalid_language(self):
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, 'invalid_language', self.intent, 5, 60)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, '', self.intent, 5, 60)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, None, self.intent, 5, 60)

    def test_invalid_intent(self):
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, '', 5, 60)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, None, 5, 60)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, 2, 5, 60)

    def test_invalid_n_sentences(self):
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, self.intent, '1', 60)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, self.intent, None, 60)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, self.intent, -3, 60)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, self.intent, 11111111, 60)

    def test_invalid_percentage_replace(self):
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, self.intent, 4, 'a')
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, self.intent, 4, None)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, self.intent, 4, -2)
        with self.assertRaises(ValidationError):
            _intent_sentence_suggestion(self.authorization, self.language, self.intent, 4, 101)

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
        'bothub_nlp_api.handlers.intent_sentence_suggestion.celery_app.send_task',
        return_value=MockAsyncResult(fake_id=0),
    )
    def test_default(self, *args):
        _intent_sentence_suggestion(
            self.authorization,
            self.language,
            self.intent,
            5,
            60,
        )

