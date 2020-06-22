from celery.result import AsyncResult

from bothub_nlp_api import utils

TRAIN_STATUS_TRAINED = "trained"
TRAIN_STATUS_FAILED = "failed"
TRAIN_STATUS_NOT_READY_FOR_TRAIN = "not_ready_for_train"


def task_queue_handler(id_task, from_queue):
    if from_queue == "celery":
        res = AsyncResult(id_task)
        status = {"PENDING": 0, "STARTED": 1, "RETRY": 1, "FAILURE": 3, "SUCCESS": 2}
        return {"status": int(status.get(res.status)), "ml_units": 0}
    if from_queue == "ai-platform":
        res = utils.get_train_job_status(id_task)
        return {
            "status": res.get("state"),
            "ml_units": res.get("trainingOutput", {}).get("consumedMLUnits", 0),
        }
    return {"status": "", "ml_units": 0}
