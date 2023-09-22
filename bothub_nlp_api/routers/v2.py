from fastapi import Depends, Header, HTTPException
from starlette.requests import Request
from bothub_nlp_api import settings
from bothub_nlp_api.api_router import CustomAPIRouter

from bothub_nlp_api.exceptions.question_answering_exceptions import (
    QuestionAnsweringException, TokenLimitException
)

from bothub_nlp_api.handlers import (
    evaluate,
    task_queue,
    parse,
    debug_parse,
    sentence_suggestion,
    intent_sentence_suggestion,
    word_suggestion,
    words_distribution,
    train,
    question_answering,
)

from bothub_nlp_api.models import (
    ParseRequest,
    ParseResponse,
    DebugParseRequest,
    DebugParseResponse,
    WordsDistributionRequest,
    SentenceSuggestionRequest,
    SentenceSuggestionResponse,
    IntentSentenceSuggestionRequest,
    IntentSentenceSuggestionResponse,
    WordSuggestionRequest,
    WordSuggestionResponse,
    WordsDistributionResponse,
    TrainRequest,
    TrainResponse,
    EvaluateRequest,
    EvaluateResponse,
    TaskQueueResponse,
    QuestionAnsweringResponse,
    QuestionAnsweringRequest,
)

from bothub_nlp_api.utils import (
    backend,
    AuthorizationRequired,
    repository_authorization_validation,
)


router = CustomAPIRouter()


@router.post(r"/parse/", response_model=ParseResponse)
async def parsepost_handler(
    item: ParseRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
    user_agent: str = Header(None),
):

    return parse._parse(
        Authorization,
        item.text,
        item.language,
        item.rasa_format,
        item.repository_version,
        user_agent=user_agent,
        from_backend=item.from_backend,
    )


@router.options(r"/parse/", status_code=204, include_in_schema=False)
async def parse_options():
    return {}  # pragma: no cover


@router.post(r"/debug_parse/", response_model=DebugParseResponse)
async def debug_parsepost_handler(
    item: DebugParseRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):

    return debug_parse._debug_parse(
        Authorization, item.text, item.language, item.repository_version
    )


@router.options(r"/debug_parse/", status_code=204, include_in_schema=False)
async def debug_parse_options():
    return {}  # pragma: no cover


@router.post(r"/sentence_suggestion/", response_model=SentenceSuggestionResponse)
async def sentence_suggestion_post_handler(item: SentenceSuggestionRequest,):

    return sentence_suggestion._sentence_suggestion(
        item.text,
        item.language,
        item.n_sentences_to_generate,
        item.percentage_to_replace,
    )


@router.options(r"/sentence_suggestion/", status_code=204, include_in_schema=False)
async def sentence_suggestion_options():
    return {}  # pragma: no cover


@router.post(
    r"/intent_sentence_suggestion/", response_model=IntentSentenceSuggestionResponse
)
async def intent_sentence_suggestion_post_handler(
    item: IntentSentenceSuggestionRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):

    return intent_sentence_suggestion._intent_sentence_suggestion(
        Authorization,
        item.language,
        item.intent,
        item.n_sentences_to_generate,
        item.percentage_to_replace,
        item.repository_version,
    )


@router.options(
    r"/intent_sentence_suggestion/", status_code=204, include_in_schema=False
)
async def intent_sentence_suggestion_options():
    return {}  # pragma: no cover


@router.post(r"/word_suggestion/", response_model=WordSuggestionResponse)
async def word_suggestion_post_handler(item: WordSuggestionRequest,):

    return word_suggestion._word_suggestion(
        item.text, item.language, item.n_words_to_generate
    )


@router.options(r"/word_suggestion/", status_code=204, include_in_schema=False)
async def word_suggestion_options():
    return {}  # pragma: no cover


@router.post(r"/words_distribution/", response_model=WordsDistributionResponse)
async def words_distribution_post_handler(
    item: WordsDistributionRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    return words_distribution._words_distribution(
        Authorization, item.language, item.repository_version
    )


@router.options(r"/words_distribution/", status_code=204, include_in_schema=False)
async def words_distribution_options():
    return {}  # pragma: no cover


@router.post(r"/train/", response_model=TrainResponse)
async def train_handler(
    item: TrainRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    result = train.train_handler(Authorization, item.repository_version, item.language)
    if result.get("status") and result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.options(r"/train/", status_code=204, include_in_schema=False)
async def train_options():
    return {}  # pragma: no cover


@router.get(r"/info/")
async def info_handler(
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    repository_authorization = repository_authorization_validation(Authorization)
    info = backend().request_backend_info(repository_authorization)
    if info.get("detail"):
        raise HTTPException(status_code=400, detail=info)
    return info


@router.options(r"/info/", status_code=204, include_in_schema=False)
async def info_options():
    return {}  # pragma: no cover


@router.post(r"/evaluate/", response_model=EvaluateResponse)
async def evaluate_handler(
    item: EvaluateRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    if item.cross_validation:
        result = evaluate.crossvalidation_evaluate_handler(
            Authorization, item.language, item.repository_version
        )
    else:
        result = evaluate.evaluate_handler(
            Authorization, item.language, item.repository_version
        )
    if result.get("status") and result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.options(r"/evaluate/", status_code=204, include_in_schema=False)
async def evaluate_options():
    return {}  # pragma: no cover


@router.get(r"/task-queue/", response_model=TaskQueueResponse)
async def task_queue_handler(id_task: str, from_queue: str):

    return task_queue.task_queue_handler(id_task, from_queue)


if settings.BOTHUB_NLP_API_ENABLE_QA_ROUTE:
    @router.post(r"/question-answering/", response_model=QuestionAnsweringResponse)
    async def question_answering_handler(
        item: QuestionAnsweringRequest,
        request: Request = Depends(AuthorizationRequired()),
        authorization: str = Header(..., description="Bearer your_key"),
        user_agent: str = Header(None),
    ):
        try:
            result = question_answering.qa_handler(
                authorization,
                item.knowledge_base_id,
                item.question,
                item.language,
                user_agent=user_agent,
                from_backend=item.from_backend,
            )
        except TokenLimitException as err:
            raise HTTPException(status_code=400, detail=err.__dict__)
        except QuestionAnsweringException as err:
            raise HTTPException(status_code=400, detail=err.__str__())
        if result.get("status") and result.get("error"):
            raise HTTPException(status_code=400, detail=result)

        return result
