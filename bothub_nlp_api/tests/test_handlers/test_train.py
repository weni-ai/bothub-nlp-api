import unittest
from unittest.mock import patch

from bothub_nlp_api.utils import (
    AuthorizationIsRequired,
    ValidationError,
)
from bothub_nlp_api.handlers.train import train_handler


class TestTrainHandler(unittest.TestCase):
    def setUp(self):
        self.authorization = 'Bearer aa11a1a1-111a-111a-11a1-aaa1a11aa111'
        self.repository_version = 299
        self.language = 'pt_br'

    def test_invalid_auth(self):
        with self.assertRaises(AuthorizationIsRequired):
            train_handler('', self.repository_version, "pt_br")
        with self.assertRaises(AuthorizationIsRequired):
            train_handler(None, self.repository_version, "pt_br")
        with self.assertRaises(AuthorizationIsRequired):
            train_handler(3, self.repository_version, "pt_br")

    def test_invalid_language(self):
        with self.assertRaises(ValidationError):
            train_handler(self.authorization, self.repository_version, "invalid_language")
        with self.assertRaises(ValidationError):
            train_handler(self.authorization, self.repository_version, 3)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_all_readytotrain_languages',
        return_value=[
            {
                "current_version_id": 1,
                "repository_authorization_user_id": 1,
                "language": 'pt_br',
                "algorithm": 'transformer_network_diet_bert',
                "use_name_entities": False,
                "use_competing_intents": False,
                "use_analyze_char": False,
            },
            {
                "current_version_id": 2,
                "repository_authorization_user_id": 1,
                "language": 'en',
                "algorithm": 'transformer_network_diet_bert',
                "use_name_entities": False,
                "use_competing_intents": False,
                "use_analyze_char": False,
            },
        ],
    )
    @patch('bothub_nlp_api.handlers.train.settings.BOTHUB_SERVICE_TRAIN', "ai-platform")
    @patch(
        'bothub_nlp_api.handlers.train.send_job_train_ai_platform',
        return_value={},
    )
    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_save_queue_id',
        return_value={},
    )
    @patch(
        'bothub_nlp_api.handlers.train.settings.SUPPORTED_LANGUAGES',
        {
            "pt_br": "pt_br",
            "en": "en",
        },
    )
    def test_default(self, *args):
        r = train_handler(self.authorization, self.repository_version)
        expected = {
            'SUPPORTED_LANGUAGES': ['pt_br', 'en'],
            'languages_report': {
                'pt_br': {'status': 'processing'},
                'en': {'status': 'processing'}
            }
        }
        self.assertEqual(r, expected)

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_train',
        return_value={
            "ready_for_train": True,
            "current_version_id": 1,
            "repository_authorization_user_id": 1,
            "language": 'pt_br',
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    @patch('bothub_nlp_api.handlers.train.settings.BOTHUB_SERVICE_TRAIN', "ai-platform")
    @patch(
        'bothub_nlp_api.handlers.train.send_job_train_ai_platform',
        return_value={},
    )
    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_save_queue_id',
        return_value={},
    )
    @patch(
        'bothub_nlp_api.handlers.train.settings.SUPPORTED_LANGUAGES',
        {
            "pt_br": "pt_br",
            "en": "en",
        },
    )
    def test_specific_language(self, *args):
        r = train_handler(self.authorization, self.repository_version, "pt_br")
        expected = {
            'SUPPORTED_LANGUAGES': ['pt_br', 'en'],
            'languages_report': {
                'pt_br': {'status': 'processing'}
            }
        }
        self.assertEqual(r, expected)
