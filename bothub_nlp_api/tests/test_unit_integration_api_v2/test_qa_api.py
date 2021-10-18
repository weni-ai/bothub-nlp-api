import os
import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestParseRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)
        self.header = {"Authorization": "Bearer aa11a1a1-111a-111a-11a1-aaa1a11aa111"}

    def test_v2_invalid_authorization(self):

        invalid_header = {"Authorization": ""}
        response = self.app.post("v2/question-answering", headers=invalid_header)
        self.assertEqual(401, response.status_code)

        invalid_header = {}
        response = self.app.post("v2/question-answering", headers=invalid_header)
        self.assertEqual(422, response.status_code)

    def test_v2_missing_id(self):
        invalid_body = {"question": "test", "language": "en"}
        response = self.app.post("v2/question-answering", headers=self.header, json=invalid_body)
        self.assertEqual(422, response.status_code)

    def test_v2_missing_question(self):
        invalid_body = {"language": "en", "knowledge_base_id": 1}
        response = self.app.post("v2/question-answering", headers=self.header, json=invalid_body)
        self.assertEqual(422, response.status_code)

    def test_v2_missing_language(self):
        invalid_body = {"language": "en", "knowledge_base_id": 1}
        response = self.app.post("v2/question-answering", headers=self.header, json=invalid_body)
        self.assertEqual(422, response.status_code)

    @patch(
        "bothub_nlp_api.handlers.question_answering.qa_handler",
        return_value={
            "answers": [
                {"text": "response1", "confidence": 1.0},
                {"text": "response2", "confidence": 1.0},
            ],
            "id": "0",
        },
    )
    def test_v2_qa(self, *args):
        body = {"question": "test", "language": "en", "knowledge_base_id": 1}
        response = self.app.post("v2/question-answering", headers=self.header, json=body)
        self.assertEqual(200, response.status_code)
