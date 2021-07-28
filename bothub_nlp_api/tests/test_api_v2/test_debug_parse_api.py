import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestDebugParseRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)
        self.header = {
            'Authorization': 'Bearer aa11a1a1-111a-111a-11a1-aaa1a11aa111'
        }

    def test_v2_invalid_authorization(self):
        invalid_header = {"Authorization": ""}
        response = self.app.post("v2/debug_parse", headers=invalid_header)
        self.assertEqual(401, response.status_code)

        invalid_header = {}
        response = self.app.post("v2/debug_parse", headers=invalid_header)
        self.assertEqual(422, response.status_code)

    def test_v2_invalid_text(self):
        body = {"language": "en"}
        response = self.app.post("v2/debug_parse", headers=self.header, json=body)
        self.assertEqual(422, response.status_code)

    def test_v2_invalid_language(self):
        body = {"text": "test"}
        response = self.app.post("v2/debug_parse", headers=self.header, json=body)
        self.assertEqual(422, response.status_code)

    @patch(
        'bothub_nlp_api.handlers.debug_parse._debug_parse',
        return_value={
            'intent': {
                'name': 'intent',
                'confidence': 1
            },
            'words': {},
            'entities': [],
            'text': 'text',
            'repository_version': 1,
            'language': 'pt',
        }
    )
    def test_v2_debug_parse(self, *args):
        body = {"text": "test", "language": "en"}
        response = self.app.post("v2/debug_parse", headers=self.header, json=body)
        self.assertEqual(200, response.status_code)
