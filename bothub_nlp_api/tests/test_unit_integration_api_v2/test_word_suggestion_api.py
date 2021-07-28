import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestWordSuggestionRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)

    def test_v2_invalid_text(self):
        invalid_body = {"language": "en"}
        response = self.app.post("v2/word_suggestion", headers={}, json=invalid_body)
        self.assertEqual(422, response.status_code)

    def test_v2_invalid_language(self):
        invalid_body = {"text": "test"}
        response = self.app.post("v2/word_suggestion", headers={}, json=invalid_body)
        self.assertEqual(422, response.status_code)

    @patch(
        'bothub_nlp_api.handlers.word_suggestion._word_suggestion',
        return_value={
            'text': 'text',
            'similar_words': []
        }
    )
    def test_v2_word_suggestion(self, *args):
        body = {"text": "test", "language": "en"}
        response = self.app.post("v2/word_suggestion", headers={}, json=body)
        self.assertEqual(200, response.status_code)
