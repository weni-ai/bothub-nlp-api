import unittest
from unittest.mock import patch
from bothub_nlp_api.utils import ValidationError, AuthorizationIsRequired

from bothub_nlp_api.handlers.parse import validate_language, _parse


class TestParseHandler(unittest.TestCase):
    def setUp(self):
        self.authorization = 'da39f8a1-532a-459e-85c0-bfd8f96db828'
        self.repository_version = 299
        self.language = 'pt_br'
        self.text = "parse test"

    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_parse',
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": 'pt_br',
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    def test_validate_language_default(self, *args):
        validate_language(self.language, self.authorization, self.repository_version)

    @patch(
        'bothub_nlp_api.handlers.parse.DEFAULT_LANGS_PRIORITY',
        {}
    )
    @patch(
        'bothub_backend.bothub.BothubBackend.request_backend_parse',
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": 'pt_br',
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    def test_validate_language(self, *args):
        validate_language(self.language, self.authorization, self.repository_version)

    def test_validate_incorrect_language(self, *args):
        with self.assertRaises(ValidationError):
            validate_language("unknown_lang", self.authorization, self.repository_version)

    def test_validate_incorrect_region(self, *args):
        validate_language("pt_zz", self.authorization, self.repository_version)

    def test_validate_no_language(self, *args):
        with self.assertRaises(ValidationError):
            validate_language(None, self.authorization, self.repository_version)

        with self.assertRaises(ValidationError):
            validate_language('', self.authorization, self.repository_version)


    @patch(
        'bothub_nlp_api.handlers.parse.validate_language',
        return_value={
            "version": True,
            "repository_version": 121212,
            "total_training_end": 1,
            "language": 'pt_br',
            "algorithm": 'transformer_network_diet_bert',
            "use_name_entities": False,
            "use_competing_intents": False,
            "use_analyze_char": False,
        },
    )
    def test_parse_default(self, *args):
        with self.assertRaises(AuthorizationIsRequired):
            _parse('', 'text', 'pt_br', self.repository_version)

        with self.assertRaises(ValidationError):
            _parse(self.authorization, '', 'pt_br', self.repository_version)
            _parse(self.authorization, None, 'pt_br', self.repository_version)
            _parse(self.authorization, 23, 'pt_br', self.repository_version)

        #_parse(self.authorization, 'text', 'pt_br',  self.repository_version)

    @patch(
        'bothub_nlp_api.handlers.parse.validate_language',
        return_value={},
    )
    def test_parse_invalid_language(self, *args):
        with self.assertRaises(ValidationError):
            _parse(self.authorization, 'text', 'pt_br', self.repository_version)

