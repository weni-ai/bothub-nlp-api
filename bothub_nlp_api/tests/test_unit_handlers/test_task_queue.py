import unittest
from unittest.mock import patch
from celery.result import AsyncResult
from bothub_nlp_api.utils import ValidationError
from bothub_nlp_api.handlers.task_queue import task_queue_handler


class MockAsyncResult(AsyncResult):
    status = 'SUCCESS'

    def __init__(self, fake_id):
        super().__init__(fake_id)

    def wait(self):
        pass


MockResponse = {
    'state': 'SUCCEEDED',
    'trainingOutput': {
        'consumedMLUnits': 2
    }
}


class TestTaskQueueHandler(unittest.TestCase):
    def setUp(self):
        self.id_task = 1

    def test_invalid_queue(self):
        with self.assertRaises(ValidationError):
            task_queue_handler(self.id_task, None)
        with self.assertRaises(ValidationError):
            task_queue_handler(self.id_task, 'invalid queue')
        with self.assertRaises(ValidationError):
            task_queue_handler(self.id_task, 3)

    @patch(
        'bothub_nlp_api.handlers.task_queue.get_train_job_status',
        return_value=MockResponse
    )
    def test_ai_platform_default(self, *args):
        task_queue_handler(self.id_task, 'ai-platform')

    @patch(
        'bothub_nlp_api.handlers.task_queue.AsyncResult',
        return_value=MockAsyncResult(fake_id='1')
    )
    def test_celery_default(self, *args):
        task_queue_handler(self.id_task, 'celery')
