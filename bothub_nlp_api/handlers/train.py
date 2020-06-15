from bothub_nlp_celery.actions import ACTION_TRAIN, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_TRAIN_UPDATE

from .. import settings
from ..utils import backend
from ..utils import get_repository_authorization

TRAIN_STATUS_TRAINED = "trained"
TRAIN_STATUS_FAILED = "failed"
TRAIN_STATUS_NOT_READY_FOR_TRAIN = "not_ready_for_train"


def train_handler(authorization, repository_version=None):
    repository_authorization = get_repository_authorization(authorization)

    languages_report = {}
    train_tasks = []

    for language in settings.SUPPORTED_LANGUAGES.keys():

        current_update = backend().request_backend_train(
            repository_authorization, language, repository_version
        )

        if not current_update.get("ready_for_train"):
            languages_report[language] = {"status": TRAIN_STATUS_NOT_READY_FOR_TRAIN}
            continue

        train_task = celery_app.send_task(
            TASK_NLU_TRAIN_UPDATE,
            args=[
                current_update.get("current_version_id"),
                current_update.get("repository_authorization_user_id"),
                repository_authorization,
            ],
            queue=queue_name(ACTION_TRAIN, current_update.get("language")),
        )
        train_tasks.append({"task": train_task, "language": language})

    for train_task in train_tasks:
        language = train_task.get("language")
        train_task["task"].wait(propagate=False)
        if train_task["task"].successful():
            languages_report[language] = {"status": TRAIN_STATUS_TRAINED}
        elif train_task["task"].failed():
            languages_report[language] = {
                "status": TRAIN_STATUS_FAILED,
                "error": str(train_task["task"].result),
            }

    resp = {
        "SUPPORTED_LANGUAGES": list(settings.SUPPORTED_LANGUAGES.keys()),
        "languages_report": languages_report,
    }
    return resp


def get_train_job_status(project_name, job_name):
    project_name = project_name
    projectId = 'projects/{}'.format(project_name)
    job_name = job_name
    jobId = '{}/jobs/{}'.format(projectId, job_name)

    cloudml = discovery.build('ml', 'v1')

    request = cloudml.projects().jobs().get(name=jobId)

    response = None

    try:
        response = request.execute()
    except errors.HttpError as e:
        raise e

    if response == None:
        raise Exception("Got None as response.")
    
    return response['state']

def get_train_job_ml_units(project_name, job_name):
    project_name = project_name
    projectId = 'projects/{}'.format(project_name)
    job_name = job_name
    jobId = '{}/jobs/{}'.format(projectId, job_name)

    cloudml = discovery.build('ml', 'v1')

    request = cloudml.projects().jobs().get(name=jobId)

    response = None

    try:
        response = request.execute()
    except errors.HttpError as e:
        raise e

    if response == None:
        raise Exception("Got None as response.")
    
    return response['trainingOutput']['consumedMLUnits']
