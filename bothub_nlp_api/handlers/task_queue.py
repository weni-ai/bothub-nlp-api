from celery.result import AsyncResult

TRAIN_STATUS_TRAINED = "trained"
TRAIN_STATUS_FAILED = "failed"
TRAIN_STATUS_NOT_READY_FOR_TRAIN = "not_ready_for_train"


def task_queue_handler(authorization, id_task, from_queue):
    if from_queue == "celery":
        res = AsyncResult(id_task)
        return {"status": res.status, "ml_units": 0}
    return {}

