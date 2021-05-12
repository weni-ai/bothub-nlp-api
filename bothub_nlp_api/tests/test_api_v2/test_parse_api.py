import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestDoc(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)
        self.header = {
            'Authorization': 'Bearer da39f8a1-532a-459e-85c0-bfd8f96db828'
        }

    def test_v2_invalid_authorization(self):
        invalid_header = {"Authorization": ""}
        response = self.app.post("v2/parse", headers=invalid_header)
        self.assertEqual(401, response.status_code)

        invalid_header = {}
        response = self.app.post("v2/parse", headers=invalid_header)
        self.assertEqual(422, response.status_code)

    def test_v2_invalid_text(self):
        body = {"language": "pt_br"}
        response = self.app.post("v2/parse", headers=self.header, json=body)
        self.assertEqual(422, response.status_code)

    @patch(
        'bothub_nlp_api.handlers.parse._parse',
        return_value={
            'intent': {
                'name': 'intent',
                'confidence': 1
            },
            'intent_ranking': [],
            'group_list': [],
            'entities_list': [],
            'entities': {},
            'text': 'text',
            'repository_version': 1,
            'language': 'pt',
        }
    )
    def test_v2_parse(self, *args):
        body = {"text": "test"}
        response = self.app.post("v2/parse", headers=self.header, json=body)
        self.assertEqual(response.status_code, 200)
