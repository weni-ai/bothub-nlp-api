import environ
from collections import OrderedDict


def cast_supported_languages(i):
    return OrderedDict([x.split(":", 1) if ":" in x else (x, x) for x in i.split("|")])


environ.Env.read_env(env_file=(environ.Path(__file__) - 2)(".env"))

env = environ.Env(
    # set casting, default value
    ENVIRONMENT=(str, "production"),
    BOTHUB_NLP_API_HOST=(str, "0.0.0.0"),
    BOTHUB_NLP_API_PORT=(int, 2657),
    BOTHUB_NLP_API_WEB_CONCURRENCY=(int, None),
    BOTHUB_NLP_API_WORKERS_PER_CORE=(float, 3),
    BOTHUB_NLP_API_LOG_LEVEL=(str, "info"),
    BOTHUB_NLP_API_KEEPALIVE=(int, 120),
    BOTHUB_NLP_SENTRY_CLIENT=(bool, False),
    BOTHUB_NLP_SENTRY=(str, None),
    SUPPORTED_LANGUAGES=(cast_supported_languages, "en|pt"),
    BOTHUB_ENGINE_URL=(str, "https://api.bothub.it"),
    BOTHUB_TORCHSERVE_URL=(str, "https://torchserve.weni.ai"),
    BOTHUB_GOOGLE_PROJECT_ID=(str, None),
    BOTHUB_GOOGLE_CREDENTIALS_REFRESH_TOKEN=(str, None),
    BOTHUB_GOOGLE_CREDENTIALS_TOKEN_URI=(str, None),
    BOTHUB_GOOGLE_CREDENTIALS_CLIENT_ID=(str, None),
    BOTHUB_GOOGLE_CREDENTIALS_CLIENT_SECRET=(str, None),
    BOTHUB_GOOGLE_AI_PLATFORM_IMAGE_VERSION=(str, "1.0.0"),
    BOTHUB_GOOGLE_AI_PLATFORM_REGISTRY=(str, "us.gcr.io/bothub/bothub-nlp-ai-platform"),
    BOTHUB_GOOGLE_AI_PLATFORM_PACKAGE_URI=(
        list,
        [
            "gs://poc-training-ai-platform/bothub-nlp-ai-platform/bothub-nlp-ai-platform-0.1.tar.gz"
        ],
    ),
    BOTHUB_GOOGLE_AI_PLATFORM_JOB_TIMEOUT=(int, None),
    BOTHUB_NLP_AWS_S3_BUCKET_NAME=(str, None),
    BOTHUB_NLP_AWS_ACCESS_KEY_ID=(str, None),
    BOTHUB_NLP_AWS_SECRET_ACCESS_KEY=(str, None),
    BOTHUB_NLP_AWS_REGION_NAME=(str, None),
    BOTHUB_NLP_API_ENABLE_QA_ROUTE=(bool, False),
    BOTHUB_NLP_API_QA_TEXT_LIMIT=(int, 25000),
    BOTHUB_NLP_API_QA_QUESTION_LIMIT=(int, 500),
    OPENAI_API_KEY=(str, None),
    WENIGPT_API_URL=(str, None),
    WENIGPT_API_TOKEN=(str, None),
    WENIGPT_COOKIE=(str, None),
    WENIGPT_SUPPORTED_LANGUAGES=(str, None),
    WENIGPT_PROMPT_INTRODUCTION=(str, "Você é um médico tratando um paciente com amnésia. Para responder as perguntas do paciente, você irá ler um texto anteriormente para se contextualizar. Se você trouxer informações desconhecidas, fora do texto lido, poderá deixar o paciente confuso. Se o paciente fizer uma questão sobre informações não presentes no texto, você precisa responder 'Desculpe, não possuo essa informação', pois se tentar responder, pode trazer informações que não ajudarão o paciente recuperar sua memória.\\n\\n"),
    WENIGPT_PROMPT_TEXT=(str, "TEXTO: "),
    WENIGPT_PROMPT_QUESTION=(str, "\\n\\nPERGUNTA: "),
    WENIGPT_PROMPT_REINFORCEMENT_INSTRUCTION=(str, "Lembre, se não estiver no texto ou não souber a resposta, responda especificamente 'Desculpe, não possuo essa informação'. Precisamos ajudar o paciente.\\n\\n"),
    WENIGPT_PROMPT_ANSWER=(str, "RESPOSTA:"),
    WENIGPT_MAX_NEW_TOKENS=(int, 1000),
    WENIGPT_TOP_P=(float, 0.1),
    WENIGPT_TEMPERATURE=(float, 0.1),
    WENIGPT_STOP_SEQUENCES=(list, ["PERGUNTA:", "RESPOSTA:"])
)

ENVIRONMENT = env.str("ENVIRONMENT")
BOTHUB_NLP_API_HOST = env.str("BOTHUB_NLP_API_HOST")
BOTHUB_NLP_API_PORT = env.int("BOTHUB_NLP_API_PORT")
BOTHUB_NLP_API_WEB_CONCURRENCY = env.int("BOTHUB_NLP_API_WEB_CONCURRENCY")
BOTHUB_NLP_API_WORKERS_PER_CORE = env.float("BOTHUB_NLP_API_WORKERS_PER_CORE")
BOTHUB_NLP_API_LOG_LEVEL = env.str("BOTHUB_NLP_API_LOG_LEVEL")
BOTHUB_NLP_API_KEEPALIVE = env.int("BOTHUB_NLP_API_KEEPALIVE")

# QA Route prototype activation
BOTHUB_NLP_API_ENABLE_QA_ROUTE = env.bool("BOTHUB_NLP_API_ENABLE_QA_ROUTE")
BOTHUB_NLP_API_QA_TEXT_LIMIT = env.int("BOTHUB_NLP_API_QA_TEXT_LIMIT")
BOTHUB_NLP_API_QA_QUESTION_LIMIT = env.int("BOTHUB_NLP_API_QA_QUESTION_LIMIT")

# Sentry

BOTHUB_NLP_SENTRY_CLIENT = env.bool("BOTHUB_NLP_SENTRY_CLIENT")
BOTHUB_NLP_SENTRY = env.str("BOTHUB_NLP_SENTRY")

SUPPORTED_LANGUAGES = env.get_value(
    "SUPPORTED_LANGUAGES", cast_supported_languages, "en|pt", True
)

BOTHUB_ENGINE_URL = env.str("BOTHUB_ENGINE_URL")
BOTHUB_TORCHSERVE_URL = env.str("BOTHUB_TORCHSERVE_URL")

BOTHUB_SERVICE_TRAIN = env.str("BOTHUB_SERVICE_TRAIN", default="celery")

# Google Credentials Ai Platform
BOTHUB_GOOGLE_PROJECT_ID = env.str("BOTHUB_GOOGLE_PROJECT_ID")
BOTHUB_GOOGLE_CREDENTIALS_REFRESH_TOKEN = env.str(
    "BOTHUB_GOOGLE_CREDENTIALS_REFRESH_TOKEN"
)
BOTHUB_GOOGLE_CREDENTIALS_TOKEN_URI = env.str("BOTHUB_GOOGLE_CREDENTIALS_TOKEN_URI")
BOTHUB_GOOGLE_CREDENTIALS_CLIENT_ID = env.str("BOTHUB_GOOGLE_CREDENTIALS_CLIENT_ID")
BOTHUB_GOOGLE_CREDENTIALS_CLIENT_SECRET = env.str(
    "BOTHUB_GOOGLE_CREDENTIALS_CLIENT_SECRET"
)
BOTHUB_GOOGLE_AI_PLATFORM_IMAGE_VERSION = env.str(
    "BOTHUB_GOOGLE_AI_PLATFORM_IMAGE_VERSION"
)
BOTHUB_GOOGLE_AI_PLATFORM_REGISTRY = env.str("BOTHUB_GOOGLE_AI_PLATFORM_REGISTRY")
BOTHUB_GOOGLE_AI_PLATFORM_PACKAGE_URI = env.list(
    "BOTHUB_GOOGLE_AI_PLATFORM_PACKAGE_URI"
)

BOTHUB_GOOGLE_AI_PLATFORM_JOB_TIMEOUT = env.int("BOTHUB_GOOGLE_AI_PLATFORM_JOB_TIMEOUT")

BOTHUB_NLP_AWS_S3_BUCKET_NAME = env.str("BOTHUB_NLP_AWS_S3_BUCKET_NAME")
BOTHUB_NLP_AWS_ACCESS_KEY_ID = env.str("BOTHUB_NLP_AWS_ACCESS_KEY_ID")
BOTHUB_NLP_AWS_SECRET_ACCESS_KEY = env.str("BOTHUB_NLP_AWS_SECRET_ACCESS_KEY")
BOTHUB_NLP_AWS_REGION_NAME = env.str("BOTHUB_NLP_AWS_REGION_NAME")

# OpenAI

OPENAI_API_KEY = env.str("OPENAI_API_KEY")

# WeniGPT

WENIGPT_API_URL = env.str("WENIGPT_API_URL")
WENIGPT_API_TOKEN = env.str("WENIGPT_API_TOKEN")
WENIGPT_COOKIE = env.str("WENIGPT_COOKIE")
WENIGPT_SUPPORTED_LANGUAGES = env.str("WENIGPT_SUPPORTED_LANGUAGES")

# wenigpt most dinamic prompt
WENIGPT_PROMPT_INTRODUCTION = env.str("WENIGPT_PROMPT_INTRODUCTION")
WENIGPT_PROMPT_TEXT = env.str("WENIGPT_PROMPT_TEXT")
WENIGPT_PROMPT_QUESTION = env.str("WENIGPT_PROMPT_QUESTION")
WENIGPT_PROMPT_REINFORCEMENT_INSTRUCTION = env.str("WENIGPT_PROMPT_REINFORCEMENT_INSTRUCTION")
WENIGPT_PROMPT_ANSWER = env.str("WENIGPT_PROMPT_ANSWER")

# wenigpt most dinamic sampling_params
WENIGPT_MAX_NEW_TOKENS = env.int("WENIGPT_MAX_NEW_TOKENS")
WENIGPT_TOP_P = env.float("WENIGPT_TOP_P")
WENIGPT_TEMPERATURE = env.float("WENIGPT_TEMPERATURE")
WENIGPT_STOP_SEQUENCES = env.list("WENIGPT_STOP_SEQUENCES")