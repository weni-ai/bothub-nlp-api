from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_QUESTION_ANSWERING
from bothub_nlp_celery.actions import ACTION_QUESTION_ANSWERING, queue_name


def qa_handler(context, question, language):
    # TODO: Repository Authentication

    answer_task = celery_app.send_task(
        TASK_NLU_QUESTION_ANSWERING,
        args=[
            context,
            question,
        ],
        queue=queue_name(language, ACTION_QUESTION_ANSWERING, "QA"),
    )
    answer_task.wait()
    answer = answer_task.result

    return answer
