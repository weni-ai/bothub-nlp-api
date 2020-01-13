import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api


class TestDoc(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)

    def test_base(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
