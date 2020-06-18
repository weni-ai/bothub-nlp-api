from celery.result import AsyncResult
from bothub_nlp_celery.actions import ACTION_TRAIN, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE

from .. import settings
from ..utils import backend
from ..utils import get_repository_authorization

TRAIN_STATUS_TRAINED = "trained"
TRAIN_STATUS_FAILED = "failed"
TRAIN_STATUS_NOT_READY_FOR_TRAIN = "not_ready_for_train"


def task_queue_handler(authorization, id_task, from_queue):
    repository_authorization = get_repository_authorization(authorization)
    res = AsyncResult(id_task)

    return {"status": res.status, "ml_units": 0}
