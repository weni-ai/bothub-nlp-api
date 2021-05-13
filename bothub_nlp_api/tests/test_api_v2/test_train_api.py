import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestTrainRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)
        self.header = {
            'Authorization': 'Bearer da39f8a1-532a-459e-85c0-bfd8f96db828'
        }

    def test_v2_invalid_authorization(self):
        invalid_header = {"Authorization": ""}
        response = self.app.post("v2/train", headers=invalid_header)
        self.assertEqual(401, response.status_code)

        invalid_header = {}
        response = self.app.post("v2/train", headers=invalid_header)
        self.assertEqual(422, response.status_code)

    @patch(
        'bothub_nlp_api.handlers.train.train_handler',
        return_value={
            'SUPPORTED_LANGUAGES': [],
            'languages_report': {}
        }
    )
    def test_v2_train(self, *args):
        body = {"intent": "test", "language": "en"}
        response = self.app.post("v2/train", headers=self.header, json=body)
        self.assertEqual(200, response.status_code)
