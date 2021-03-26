from fastapi import Depends, APIRouter, Header, HTTPException
from starlette.requests import Request

from bothub_nlp_api.handlers import evaluate
from bothub_nlp_api.handlers import task_queue
from bothub_nlp_api.handlers import parse
from bothub_nlp_api.handlers import debug_parse
from bothub_nlp_api.handlers import sentence_suggestion
from bothub_nlp_api.handlers import intent_sentence_suggestion
from bothub_nlp_api.handlers import word_suggestion
from bothub_nlp_api.handlers import words_distribution
from bothub_nlp_api.handlers import train
from bothub_nlp_api.models import (
    ParseRequest,
    DebugParseRequest,
    WordsDistributionRequest,
    SentenceSuggestionRequest,
    IntentSentenceSuggestionRequest,
    WordSuggestionRequest,
    WordsDistributionResponse,
    TrainRequest,
    EvaluateRequest,
    TaskQueueResponse,
)
from bothub_nlp_api.models import ParseResponse
from bothub_nlp_api.models import DebugParseResponse
from bothub_nlp_api.models import SentenceSuggestionResponse
from bothub_nlp_api.models import IntentSentenceSuggestionResponse
from bothub_nlp_api.models import WordSuggestionResponse
from bothub_nlp_api.models import TrainResponse
from bothub_nlp_api.models import EvaluateResponse
from bothub_nlp_api.utils import backend, AuthorizationRequired
from bothub_nlp_api.utils import get_repository_authorization

router = APIRouter(redirect_slashes=False)


@router.post(r"/parse/?", response_model=ParseResponse)
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


@router.options(r"/parse/?", status_code=204, include_in_schema=False)
async def parse_options():
    return {}  # pragma: no cover


@router.post(r"/debug_parse/?", response_model=DebugParseResponse)
async def debug_parsepost_handler(
    item: DebugParseRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):

    return debug_parse._debug_parse(
        Authorization, item.text, item.language, item.repository_version
    )


@router.options(r"/debug_parse/?", status_code=204, include_in_schema=False)
async def debug_parse_options():
    return {}  # pragma: no cover


@router.post(r"/sentence_suggestion/?", response_model=SentenceSuggestionResponse)
async def sentence_suggestion_post_handler(item: SentenceSuggestionRequest,):

    return sentence_suggestion._sentence_suggestion(
        item.text,
        item.language,
        item.n_sentences_to_generate,
        item.percentage_to_replace,
        item.intent,
    )


@router.options(r"/sentence_suggestion/?", status_code=204, include_in_schema=False)
async def sentence_suggestion_options():
    return {}  # pragma: no cover


@router.post(
    r"/intent_sentence_suggestion/?", response_model=IntentSentenceSuggestionResponse
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
    r"/intent_sentence_suggestion/?", status_code=204, include_in_schema=False
)
async def intent_sentence_suggestion_options():
    return {}  # pragma: no cover


@router.post(r"/word_suggestion/?", response_model=WordSuggestionResponse)
async def word_suggestion_post_handler(item: WordSuggestionRequest,):

    return word_suggestion._word_suggestion(
        item.text, item.language, item.n_words_to_generate
    )


@router.options(r"/word_suggestion/?", status_code=204, include_in_schema=False)
async def word_suggestion_options():
    return {}  # pragma: no cover


@router.post(r"/words_distribution/?", response_model=WordsDistributionResponse)
async def words_distribution_post_handler(
    item: WordsDistributionRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    return words_distribution._words_distribution(
        Authorization, item.language, item.repository_version
    )


@router.options(r"/words_distribution/?", status_code=204, include_in_schema=False)
async def words_distribution_options():
    return {}  # pragma: no cover


@router.post(r"/train/?", response_model=TrainResponse)
async def train_handler(
    item: TrainRequest,
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    result = train.train_handler(Authorization, item.repository_version)
    if result.get("status") and result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.options(r"/train/?", status_code=204, include_in_schema=False)
async def train_options():
    return {}  # pragma: no cover


# @router.get(r"/info/?", response_model=InfoResponse)
@router.get(r"/info/?")
async def info_handler(
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    repository_authorization = get_repository_authorization(Authorization)
    info = backend().request_backend_info(repository_authorization)
    if info.get("detail"):
        raise HTTPException(status_code=400, detail=info)
    return info


@router.options(r"/info/?", status_code=204, include_in_schema=False)
async def info_options():
    return {}  # pragma: no cover


@router.post(r"/evaluate/?", response_model=EvaluateResponse)
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


@router.options(r"/evaluate/?", status_code=204, include_in_schema=False)
async def evaluate_options():
    return {}  # pragma: no cover


@router.get(r"/task-queue/?", response_model=TaskQueueResponse)
async def task_queue_handler(id_task: str, from_queue: str):

    return task_queue.task_queue_handler(id_task, from_queue)
