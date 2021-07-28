import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestIntentSentenceSuggestionRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)
        self.header = {
            'Authorization': 'Bearer aa11a1a1-111a-111a-11a1-aaa1a11aa111'
        }

    def test_v2_invalid_authorization(self):
        invalid_header = {"Authorization": ""}
        response = self.app.post("v2/intent_sentence_suggestion", headers=invalid_header)
        self.assertEqual(401, response.status_code)

        invalid_header = {}
        response = self.app.post("v2/intent_sentence_suggestion", headers=invalid_header)
        self.assertEqual(422, response.status_code)

    def test_v2_invalid_intent(self):
        invalid_body = {"language": "en"}
        response = self.app.post("v2/intent_sentence_suggestion", headers=self.header, json=invalid_body)
        self.assertEqual(422, response.status_code)

    def test_v2_invalid_language(self):
        invalid_body = {"intent": "test"}
        response = self.app.post("v2/intent_sentence_suggestion", headers=self.header, json=invalid_body)
        self.assertEqual(422, response.status_code)

    @patch(
        'bothub_nlp_api.handlers.intent_sentence_suggestion._intent_sentence_suggestion',
        return_value={
            'intent': 'text',
            'suggested_sentences': []
        }
    )
    def test_v2_intent_sentence_suggestion(self, *args):
        body = {"intent": "test", "language": "en"}
        response = self.app.post("v2/intent_sentence_suggestion", headers=self.header, json=body)
        self.assertEqual(200, response.status_code)
