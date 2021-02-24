from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_QUESTION_ANSWERING
from bothub_nlp_celery.actions import ACTION_QUESTION_ANSWERING, queue_name


class LargeContextException(Exception):
    def __init__(self, context_length, message="Invalid context length (over 25000 characters)"):
        self.context_length = context_length
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.context_length} characters -> {self.message}'


def qa_handler(context, question, language):
    # TODO: Repository Authentication

    if len(context) >= 25000:
        raise LargeContextException(len(context))

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
