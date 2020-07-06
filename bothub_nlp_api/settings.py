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
)

ENVIRONMENT = env.str("ENVIRONMENT")
BOTHUB_NLP_API_HOST = env.str("BOTHUB_NLP_API_HOST")
BOTHUB_NLP_API_PORT = env.int("BOTHUB_NLP_API_PORT")
BOTHUB_NLP_API_WEB_CONCURRENCY = env.int("BOTHUB_NLP_API_WEB_CONCURRENCY")
BOTHUB_NLP_API_WORKERS_PER_CORE = env.float("BOTHUB_NLP_API_WORKERS_PER_CORE")
BOTHUB_NLP_API_LOG_LEVEL = env.str("BOTHUB_NLP_API_LOG_LEVEL")
BOTHUB_NLP_API_KEEPALIVE = env.int("BOTHUB_NLP_API_KEEPALIVE")

# Sentry

BOTHUB_NLP_SENTRY_CLIENT = env.bool("BOTHUB_NLP_SENTRY_CLIENT")
BOTHUB_NLP_SENTRY = env.str("BOTHUB_NLP_SENTRY")

SUPPORTED_LANGUAGES = env.get_value(
    "SUPPORTED_LANGUAGES", cast_supported_languages, "en|pt", True
)

BOTHUB_ENGINE_URL = env.str("BOTHUB_ENGINE_URL")


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
