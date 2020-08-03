import json
import threading

import babel

from bothub_nlp_celery.actions import ACTION_PARSE, queue_name
from bothub_nlp_celery.app import celery_app
from bothub_nlp_celery.tasks import TASK_NLU_PARSE_TEXT
from bothub_nlp_celery.utils import ALGORITHM_TO_LANGUAGE_MODEL, choose_best_algorithm

from bothub_nlp_api import settings
from bothub_nlp_api.utils import AuthorizationIsRequired
from bothub_nlp_api.utils import ValidationError
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import get_repository_authorization


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


def _parse(
    authorization,
    text,
    language,
    rasa_format=False,
    repository_version=None,
    user_agent=None,
    from_backend=False,
):
    from ..utils import NEXT_LANGS

    if language is not None:
        if not str(language).lower() == "pt_br":
            try:
                language = str(babel.Locale.parse(language).language).lower()
            except ValueError:
                raise ValidationError(
                    "Expected only letters, got '{}'".format(language)
                )
            except babel.core.UnknownLocaleError:
                raise ValidationError(
                    "Language '{}' not supported by now.".format(language)
                )

    if language and (
        language not in settings.SUPPORTED_LANGUAGES.keys()
        and language not in NEXT_LANGS.keys()
    ):
        raise ValidationError("Language '{}' not supported by now.".format(language))

    repository_authorization = get_repository_authorization(authorization)
    if not repository_authorization:
        raise AuthorizationIsRequired()

    try:
        update = backend().request_backend_parse(
            repository_authorization, language, repository_version
        )
    except Exception:
        update = {}

    if not update.get("version"):
        next_languages = NEXT_LANGS.get(language, [])
        for next_language in next_languages:
            update = backend().request_backend_parse(
                repository_authorization, next_language, repository_version
            )
            if update.get("version"):
                break

    # chosen_algorithm = choose_best_algorithm(update.get("language"))
    chosen_algorithm = update.get('algorithm')

    if not update.get("version"):
        raise ValidationError("This repository has never been trained")
    answer_task = celery_app.send_task(
        TASK_NLU_PARSE_TEXT,
        args=[update.get("repository_version"), repository_authorization, text],
        kwargs={"rasa_format": rasa_format},
        queue=queue_name(
            update.get("language"),
            ACTION_PARSE,
            ALGORITHM_TO_LANGUAGE_MODEL[chosen_algorithm]),
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
                        "is_default": True
                        if result["name"] == answer["intent"]["name"]
                        else False,
                        "confidence": result["confidence"],
                    }
                    for result in answer.get("intent_ranking", [])
                ],
            }
        },
    )
    log.start()
    return answer
