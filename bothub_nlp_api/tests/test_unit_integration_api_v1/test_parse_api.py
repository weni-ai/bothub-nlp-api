import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestParseRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)
        self.header = {"Authorization": "Bearer aa11a1a1-111a-111a-11a1-aaa1a11aa111"}

    def test_v1_invalid_authorization(self):
        invalid_header = {"Authorization": ""}
        response = self.app.post("parse", headers=invalid_header)
        self.assertEqual(401, response.status_code)

        invalid_header = {}
        response = self.app.post("parse", headers=invalid_header)
        self.assertEqual(422, response.status_code)

    def test_v1_invalid_text(self):
        invalid_body = {"language": "en"}
        response = self.app.post("parse", headers=self.header, data=invalid_body)
        self.assertEqual(422, response.status_code)

    @patch(
        "bothub_nlp_api.handlers.parse._parse",
        return_value={
            "intent": {"name": "intent", "confidence": 1},
            "intent_ranking": [],
            "group_list": [],
            "entities_list": [],
            "entities": {},
            "text": "text",
            "repository_version": 1,
            "language": "pt",
        },
    )
    def test_v1_no_language(self, *args):
        body = {"text": "test"}
        response = self.app.post("parse", headers=self.header, data=body)
        self.assertEqual(200, response.status_code)

    @patch(
        "bothub_nlp_api.handlers.parse._parse",
        return_value={
            "intent": {"name": "intent", "confidence": 1},
            "intent_ranking": [],
            "group_list": [],
            "entities_list": [],
            "entities": {},
            "text": "text",
            "repository_version": 1,
            "language": "pt",
        },
    )
    def test_v1_parse(self, *args):
        body = {"text": "test", "language": "en"}
        response = self.app.post("parse", headers=self.header, data=body)
        self.assertEqual(200, response.status_code)
