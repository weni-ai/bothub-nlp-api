from typing import Optional

from fastapi import Depends, Form, APIRouter, Header, HTTPException
from starlette.requests import Request

from bothub_nlp_api.handlers import evaluate
from bothub_nlp_api.handlers import parse
from bothub_nlp_api.handlers import debug_parse
from bothub_nlp_api.handlers import sentence_suggestion
from bothub_nlp_api.handlers import train
from bothub_nlp_api.models import EvaluateResponse
from bothub_nlp_api.models import ParseResponse
from bothub_nlp_api.models import DebugParseResponse
from bothub_nlp_api.models import SentenceSuggestionResponse
from bothub_nlp_api.models import TrainResponse
from bothub_nlp_api.utils import AuthorizationRequired
from bothub_nlp_api.utils import backend
from bothub_nlp_api.utils import get_repository_authorization

router = APIRouter(redirect_slashes=False)


@router.post(r"/parse/?", response_model=ParseResponse)
async def parse_handler(
    text: str = Form(...),
    language: str = Form(default=None),
    rasa_format: Optional[str] = Form(default=False),
    repository_version: Optional[int] = Form(default=None),
    from_backend: Optional[bool] = Form(default=False),
    request: Request = Depends(AuthorizationRequired()),  # flake8: noqa
    Authorization: str = Header(..., description="Bearer your_key"),
    user_agent: str = Header(None),
):

    return parse._parse(
        Authorization,
        text,
        language,
        rasa_format,
        repository_version,
        user_agent,
        from_backend,
    )


@router.get(r"/parse/?", response_model=ParseResponse, deprecated=True)
async def parse_handler(
    text: str,
    language: str = None,
    rasa_format: Optional[str] = False,
    from_backend: Optional[bool] = Form(default=False),
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
    user_agent: str = Header(None),
):

    return parse._parse(
        Authorization,
        text,
        language,
        rasa_format,
        user_agent=user_agent,
        from_backend=from_backend,
    )


@router.options(r"/parse/?", status_code=204, include_in_schema=False)
async def parse_options():
    return {}  # pragma: no cover


@router.post(r"/debug_parse/?", response_model=DebugParseResponse)
async def debug_parse_handler(
    text: str = Form(...),
    language: str = Form(default=None),
    repository_version: Optional[int] = Form(default=None),
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):

    return debug_parse._debug_parse(Authorization, text, language, repository_version)


@router.options(r"/debug_parse/?", status_code=204, include_in_schema=False)
async def debug_parse_options():
    return {}  # pragma: no cover


@router.post(r"/sentence_suggestion/?", response_model=SentenceSuggestionResponse)
async def sentence_suggestion_handler(
    text: str = Form(...),
    language: str = Form(default="pt"),
    n_sentences_to_generate: int = Form(default=10),
    percentage_to_replace: float = Form(default=0.3),
):

    return sentence_suggestion._sentence_suggestion(
        text, language, n_sentences_to_generate, percentage_to_replace
    )


@router.options(r"/sentence_suggestion/?", status_code=204, include_in_schema=False)
async def sentence_suggestion_options():
    return {}  # pragma: no cover


@router.post(r"/train/?", response_model=TrainResponse)
async def train_handler(
    request: Request = Depends(AuthorizationRequired()),
    repository_version: Optional[int] = Form(default=None),
    language: Optional[str] = Form(default=None),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    result = train.train_handler(Authorization, repository_version, language)
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
    language: str = Form(default=None),
    repository_version: Optional[int] = Form(default=None),
    request: Request = Depends(AuthorizationRequired()),
    Authorization: str = Header(..., description="Bearer your_key"),
):
    result = evaluate.evaluate_handler(Authorization, language, repository_version)
    if result.get("status") and result.get("error"):
        raise HTTPException(status_code=400, detail=result)
    return result


@router.options(r"/evaluate/?", status_code=204, include_in_schema=False)
async def evaluate_options():
    return {}  # pragma: no cover
