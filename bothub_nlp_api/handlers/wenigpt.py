import threading
import json
import requests

from bothub_nlp_api.exceptions.question_answering_exceptions import (
    EmptyInputException,
    EmptyBaseException,
)
from bothub_nlp_api.utils import backend, repository_authorization_validation, wenigpt_language_validation
from bothub_nlp_api.settings import (
    WENIGPT_API_URL,
    WENIGPT_API_TOKEN,
    WENIGPT_COOKIE,
)


def wenigpt_handler(
    authorization: str,
    knowledge_base_id: int,
    question: str,
    language: str,
    from_backend: bool = False,
    user_agent: str = None,
):
    wenigpt_language_validation(str(language))
    user_base_authorization = repository_authorization_validation(authorization)

    if not question or not isinstance(question, str):
        raise EmptyInputException()

    request = backend().request_backend_knowledge_bases(user_base_authorization, knowledge_base_id, language)
    text = request.get("text")
    if not text:
        raise EmptyBaseException()

    response_gpt = request_wenigpt(text, question)
    answer = response_gpt["answers"]

    log = threading.Thread(
        target=backend().send_log_qa_nlp_parse,
        kwargs={
            "data": {
                "answer": answer,
                "confidence": 1.0,
                "question": question,
                "user_agent": user_agent,
                "nlp_log": json.dumps(response_gpt),
                "user": str(user_base_authorization),
                "knowledge_base": int(knowledge_base_id),
                "language": language,
                "from_backend": from_backend,
            }
        },
    )
    log.start()

    return response_gpt


def request_wenigpt(context, question):

    url = WENIGPT_API_URL
    token = WENIGPT_API_TOKEN
    cookie = WENIGPT_COOKIE
    base_prompt = f"Responda à pergunta com a maior sinceridade possível usando o e, se a resposta não estiver contida no CONTEXTO abaixo, diga '\''Desculpe, não possuo essa informação'\''.\n\nCONTEXTO: {context}- \n\nPergunta: {question}\n\nResposta:"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Cookie": cookie
    }
    data = {
        "input": {
            "prompt": base_prompt,
            "sampling_params": {
                "max_new_tokens": 1000,
                "top_p": 0.1,
                "temperature": 0.1,
                "do_sample": False,
                "stop_sequences": [
                    "Pergunta:",
                    "Resposta:"
                ]
            }
        }
    }

    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    except Exception as e:
        response = {"error": str(e)}

    response_json = response.json()
    text_answers = response_json["output"].get("text")

    if text_answers:
        text_answers = [{"text": answer} for answer in text_answers]
    else:
        text_answers = []

    return {"answers": text_answers, "id": "0"}
