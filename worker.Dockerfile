FROM ${BOTHUB_NLP_DOCKER_IMAGE_NAME:-ilha/bothub-nlp}:${BOTHUB_NLP_DOCKER_IMAGE_TAG:-latest}

ARG DOWNLOAD_LANGUAGES_MODELS
RUN if [ ${DOWNLOAD_LANGUAGES_MODELS} ]; \
        then python scripts/download_spacy_models.py ${DOWNLOAD_LANGUAGES_MODELS}; \
    fi
ENV DOWNLOADED_LANGUAGES_MODELS ${DOWNLOAD_LANGUAGES_MODELS}

ENTRYPOINT [ "celery", "worker", "-A", "bothub_nlp.core.celery", "-c", "1", "-l", "INFO", "-E" ]