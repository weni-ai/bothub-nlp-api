from bothub_nlp_celery.actions import ACTION_SCORE_CALCULATION, queue_name

from ..utils import backend, get_repository_authorization
from ..utils import AuthorizationIsRequired


from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_SCORE_CALCULATION


def score_handler(authorization, repository_version, language):

    repository_authorization = get_repository_authorization(authorization)

    if not repository_authorization:
        raise AuthorizationIsRequired()

    try:
        update = backend().request_backend_train(
            repository_authorization, language, repository_version
        )
    except Exception:
        update = {}

    answer_task = celery_app.send_task(
        TASK_NLU_SCORE_CALCULATION,
        args=[update.get("current_version_id"), repository_authorization],
        queue=queue_name(language, ACTION_SCORE_CALCULATION)
    )
    answer_task.wait()

    return answer_task.result




