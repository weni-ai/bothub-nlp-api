import json
import threading
import re

from bothub_nlp_celery.actions import ACTION_PARSE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT

from bothub_nlp_api import settings
from bothub_nlp_api.utils import AuthorizationIsRequired
from bothub_nlp_api.utils import ValidationError
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import get_repository_authorization
from bothub_nlp_api.utils import get_language_model

from ..utils import DEFAULT_LANGS_PRIORITY


def order_by_confidence(entities):
    return sorted(
        entities,
        key=lambda x: (x.get("confidence") is not None, x.get("confidence")),
        reverse=True,
    )


def get_entities_dict(answer):
    entities_dict = {}
    entities = answer.get("entities")
    for entity in reversed(order_by_confidence(entities)):
        group_value = entity.get("role") if entity.get("role") else "other"
        if not entities_dict.get(group_value):
            entities_dict[group_value] = []
        entities_dict[group_value].append(entity)
    return entities_dict


def validate_language(language, repository_authorization, repository_version):
    try:
        language = str(language.lower())
        language = re.split(r"[-_]", language)[0]
    except Exception:
        language = None

    if (
        language
        and language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in DEFAULT_LANGS_PRIORITY.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    # Tries to get repository by DEFAULT_LANGS (hard-coded exceptions)
    if language in DEFAULT_LANGS_PRIORITY.keys():
        priority_ordered_langs = DEFAULT_LANGS_PRIORITY.get(language)
        for lang in priority_ordered_langs:
            try:
                update = backend().request_backend_parse(
                    repository_authorization, lang, repository_version
                )
            except Exception:
                update = {}

            if update.get("total_training_end"):
                break

    # Else tries to get most generic repository ('LANG' only)
    else:
        try:
            update = backend().request_backend_parse(
                repository_authorization, language, repository_version
            )
        except Exception:
            update = {}

    return update


def _parse(
    authorization,
    text,
    language,
    rasa_format=False,
    repository_version=None,
    user_agent=None,
    from_backend=False,
):
    repository_authorization = get_repository_authorization(authorization)
    if not repository_authorization:
        raise AuthorizationIsRequired()

    update = validate_language(language, repository_authorization, repository_version)

    if not update.get("version"):
        raise ValidationError("This repository has never been trained")

    model = get_language_model(update)

    answer_task = celery_app.send_task(
        TASK_NLU_PARSE_TEXT,
        args=[update.get("repository_version"), repository_authorization, text],
        kwargs={"rasa_format": rasa_format},
        queue=queue_name(update.get("language"), ACTION_PARSE, model),
    )
    answer_task.wait()
    answer = answer_task.result
    entities_dict = get_entities_dict(answer)
    answer.update(
        {
            "text": text,
            "repository_version": update.get("repository_version"),
            "language": update.get("language"),
            "group_list": list(entities_dict.keys()),
            "entities": entities_dict,
        }
    )

    if "intent_ranking" not in answer or answer.get("intent_ranking") is None:
        answer.update({"intent_ranking": []})

    log = threading.Thread(
        target=backend().send_log_nlp_parse,
        kwargs={
            "data": {
                "text": text,
                "from_backend": from_backend,
                "user_agent": user_agent,
                "user": str(get_repository_authorization(authorization)),
                "repository_version_language": int(update.get("repository_version")),
                "nlp_log": json.dumps(answer),
                "log_intent": [
                    {
                        "intent": result["name"],
                        "is_default": result["name"] == answer["intent"]["name"],
                        "confidence": result["confidence"],
                    }
                    for result in answer.get("intent_ranking", [])
                ],
            }
        },
    )
    log.start()

    return answer
