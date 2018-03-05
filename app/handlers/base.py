""" Base handler module. """
import logging
import traceback
import json
import spacy

from tornado.web import RequestHandler
from bothub.common.models import RepositoryAuthorization

from app.settings import DEBUG


logger = logging.getLogger('bothub NLP - Base Request Handler')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Importing spacy languages...')
SPACY_LANGUAGES = {
    'en': spacy.load('en'),
    'de': spacy.load('de'),
    'es': spacy.load('es'),
    'pt': spacy.load('pt'),
    'fr': spacy.load('fr'),
    'it': spacy.load('it'),
    'nl': spacy.load('nl')
}
logger.info('Spacy languages imported.')


class BothubBaseHandler(RequestHandler):
    """
    This class is a base request handler,
    others handler will extends of this base handler.
    """

    def repository_authorization(self):
        authorization_header_value = self.request.headers.get('Authorization')
        authorization_uuid = authorization_header_value and authorization_header_value[7:]

        if not authorization_uuid:
            return False

        try:
            repository_authorization = RepositoryAuthorization.objects.get(uuid=authorization_uuid)
        except RepositoryAuthorization.DoesNotExist:
            return False

        return repository_authorization

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if 'exc_info' in kwargs and DEBUG:
            lines = []
            for line in traceback.format_exception(*kwargs['exc_info']):
                lines.append(line)
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                    'traceback': lines,
                }
            }))
        else:
            self.finish(json.dumps({
                'error': {
                    'code': status_code,
                    'message': self._reason,
                }
            }))
