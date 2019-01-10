import logging

from bothub_nlp_celery.app import celery_app
from . import settings

from . import MyDemand


logging.basicConfig(
    format='%(levelname)-8s -- %(asctime)-15s --- %(name)s - %(message)s',
    level=logging.INFO,
)

MyDemand(
    celery_app,
    api_server_address=(
        '0.0.0.0',
        settings.BOTHUB_NLP_WORKER_ON_DEMAND_API_PORT,
    ),
).run()
