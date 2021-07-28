import unittest
from starlette.testclient import TestClient
from bothub_nlp_api import app as api
from unittest.mock import patch


class TestTaskQueueRoute(unittest.TestCase):
    def setUp(self):
        self.app = TestClient(api.app)

    def test_v2_invalid_id_task(self):
        invalid_params = {"from_queue": "example"}
        response = self.app.get("v2/task-queue", params=invalid_params)
        self.assertEqual(422, response.status_code)

    def test_v2_invalid_queue(self):
        invalid_params = {"id_task": "example"}
        response = self.app.get("v2/task-queue", params=invalid_params)
        self.assertEqual(422, response.status_code)

    @patch(
        'bothub_nlp_api.handlers.task_queue.task_queue_handler',
        return_value={
            'status': 'test',
            'ml_units': 1.0
        }
    )
    def test_v2_task_queue(self, *args):
        params = {"id_task": "1", "from_queue": "celery"}
        response = self.app.get("v2/task-queue", params=params)
        self.assertEqual(200, response.status_code)
