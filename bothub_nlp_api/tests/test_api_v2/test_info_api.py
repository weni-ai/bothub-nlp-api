import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestInfoRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)
        self.header = {
            'Authorization': 'Bearer da39f8a1-532a-459e-85c0-bfd8f96db828'
        }

    def test_v2_info_invalid_auth(self):
        headers = {"Authorization": ""}
        response = self.app.get("v2/info", headers=headers)
        self.assertEqual(401, response.status_code)

        headers = {}
        response = self.app.get("v2/info", headers=headers)
        self.assertEqual(422, response.status_code)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_info',
        return_value={"intents": []},
    )
    def test_v2_info(self, *args):
        response = self.app.get("v2/info", headers=self.header)
        self.assertEqual(200, response.status_code)
