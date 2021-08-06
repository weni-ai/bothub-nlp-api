import unittest
from celery.result import AsyncResult
from unittest.mock import patch

from bothub_nlp_api.utils import ValidationError
from bothub_nlp_api.handlers.word_suggestion import _word_suggestion
from celery.exceptions import TimeLimitExceeded
from bothub_nlp_api.exceptions.celery_exceptions import CeleryTimeoutException


class MockAsyncResult(AsyncResult):
    result = {
        'id': 1,
        'version': 1,
    }

    def __init__(self, fake_id):
        super().__init__(fake_id)

    def wait(self):
        pass


class MockAsyncResultTimeout(MockAsyncResult):
    def wait(self):
        raise TimeLimitExceeded


class TestWordSuggestionHandler(unittest.TestCase):
    def setUp(self):
        self.text = 'some text'
        self.language = 'pt_br'

    def test_invalid_language(self):
        with self.assertRaises(ValidationError):
            _word_suggestion(self.text, 'invalid_language', 5)
        with self.assertRaises(ValidationError):
            _word_suggestion(self.text, '', 5)
        with self.assertRaises(ValidationError):
            _word_suggestion(self.text, None, 5)

    def test_invalid_text(self):
        with self.assertRaises(ValidationError):
            _word_suggestion('', self.language, 5)
        with self.assertRaises(ValidationError):
            _word_suggestion(3, self.language, 5)
        with self.assertRaises(ValidationError):
            _word_suggestion(None, self.language, 5)

    def test_invalid_n_words(self):
        with self.assertRaises(ValidationError):
            _word_suggestion(self.text, self.language, '1')
        with self.assertRaises(ValidationError):
            _word_suggestion(self.text, self.language, None)
        with self.assertRaises(ValidationError):
            _word_suggestion(self.text, self.language, -3)
        with self.assertRaises(ValidationError):
            _word_suggestion(self.text, self.language, 11111111)

    @patch(
        'bothub_nlp_api.handlers.word_suggestion.celery_app.send_task',
        return_value=MockAsyncResultTimeout(fake_id='0'),
    )
    def test_celery_timeout(self, *args):
        with self.assertRaises(CeleryTimeoutException):
            _word_suggestion(
                self.text,
                self.language,
                5,
            )

    @patch(
        'bothub_nlp_api.handlers.word_suggestion.celery_app.send_task',
        return_value=MockAsyncResult(fake_id='0'),
    )
    def test_default(self, *args):
        _word_suggestion(
            self.text,
            self.language,
            5,
        )

