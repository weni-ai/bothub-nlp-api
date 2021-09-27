import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestEvaluateRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)
        self.header = {"Authorization": "Bearer aa11a1a1-111a-111a-11a1-aaa1a11aa111"}

    def test_v1_invalid_authorization(self):
        invalid_header = {"Authorization": ""}
        response = self.app.post("evaluate", headers=invalid_header)
        self.assertEqual(401, response.status_code)

        invalid_header = {}
        response = self.app.post("evaluate", headers=invalid_header)
        self.assertEqual(422, response.status_code)

    def test_v1_invalid_language(self):
        invalid_body = {}
        response = self.app.post("evaluate", headers=self.header, data=invalid_body)
        self.assertEqual(422, response.status_code)

    @patch(
        "bothub_nlp_api.handlers.evaluate.evaluate_handler",
        return_value={
            "language": "en",
            "status": "x",
            "repository_version": 1,
            "evaluate_id": 1,
            "evaluate_version": 1,
            "cross_validation": False,
        },
    )
    def test_v1_evaluate(self, *args):
        body = {"language": "en"}
        response = self.app.post("evaluate", headers=self.header, data=body)
        self.assertEqual(200, response.status_code)

        body = {"language": "en", "cross_validation": False}
        response = self.app.post("evaluate", headers=self.header, data=body)
        self.assertEqual(200, response.status_code)
