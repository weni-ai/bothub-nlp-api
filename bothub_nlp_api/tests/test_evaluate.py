import unittest
from bothub_nlp_api.utils import ValidationError, AuthorizationIsRequired

from unittest.mock import patch

from bothub_nlp_api.handlers.evaluate import (
    evaluate_handler,
    crossvalidation_evaluate_handler
)


class MockAsyncResult:
    result = {
        'id': 1,
        'version': 1,
    }

    def __init__(self):
        pass

    def wait(self):
        pass


class TestTrainHandler(unittest.TestCase):
    def setUp(self):
        self.authorization = 'da39f8a1-532a-459e-85c0-bfd8f96db828'
        self.repository_version = 299
        self.language = 'pt_br'

    def test_invalid_input(self):
        with self.assertRaises(ValidationError):
            evaluate_handler(self.authorization, "unknown_lang", self.repository_version)
            evaluate_handler(self.authorization, None, self.repository_version)
            crossvalidation_evaluate_handler(self.authorization, "unknown_lang", self.repository_version)
            crossvalidation_evaluate_handler(self.authorization, None, self.repository_version)

        with self.assertRaises(AuthorizationIsRequired):
            evaluate_handler('', "en", self.repository_version)
            evaluate_handler(None, "en", self.repository_version)
            crossvalidation_evaluate_handler('', "en", self.repository_version)
            crossvalidation_evaluate_handler(None, "en", self.repository_version)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_evaluate',
        return_value={},
    )
    def test_evaluate_untrained_model(self, *args):
        with self.assertRaises(ValidationError):
            evaluate_handler(self.authorization, "en", self.repository_version)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_start_automatic_evaluate',
        return_value={},
    )
    def test_automatic_evaluate_invalid_model(self, *args):
        with self.assertRaises(ValidationError):
            crossvalidation_evaluate_handler(self.authorization, "en", self.repository_version)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_start_automatic_evaluate',
        return_value={
            "language": 'en',
            "repository_version_language_id": 1,
            "user_id": 1,
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
            "can_run_automatic_evaluate": False,
        },
    )
    def test_automatic_evaluate_invalid_model2(self, *args):
        with self.assertRaises(ValidationError):
            crossvalidation_evaluate_handler(self.authorization, "en", self.repository_version)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_evaluate',
        return_value={
            "update": True,
            "repository_version": 1,
            "language": 'en',
            "user_id": 1,
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch(
        'bothub_nlp_api.handlers.evaluate.celery_app.send_task',
        return_value=MockAsyncResult(),
    )
    def test_evaluate_mocked_celery(self, *args):
        evaluate_handler(self.authorization, "en", self.repository_version)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_start_automatic_evaluate',
        return_value={
            "language": 'en',
            "repository_version_language_id": 1,
            "user_id": 1,
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
            "can_run_automatic_evaluate": True,
        },
    )
    @patch(
        'bothub_nlp_api.handlers.evaluate.send_job_train_ai_platform',
        return_value={},
    )
    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_save_queue_id',
        return_value={},
    )
    def test_automatic_evaluate_mocked_celery(self, *args):
        crossvalidation_evaluate_handler(self.authorization, "en", self.repository_version)


