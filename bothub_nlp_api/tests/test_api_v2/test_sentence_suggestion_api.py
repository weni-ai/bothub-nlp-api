import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestSentenceSuggestionRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)

    def test_v2_invalid_text(self):
        body = {"language": "en"}
        response = self.app.post("v2/sentence_suggestion", headers={}, json=body)
        self.assertEqual(422, response.status_code)

    def test_v2_invalid_language(self):
        body = {"text": "test"}
        response = self.app.post("v2/sentence_suggestion", headers={}, json=body)
        self.assertEqual(422, response.status_code)

    @patch(
        'bothub_nlp_api.handlers.sentence_suggestion._sentence_suggestion',
        return_value={
            'text': 'text',
            'suggested_sentences': []
        }
    )
    def test_v2_sentence_suggestion(self, *args):
        body = {"text": "test", "language": "en"}
        response = self.app.post("v2/sentence_suggestion", headers={}, json=body)
        self.assertEqual(200, response.status_code)
