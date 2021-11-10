# Bothub NLP - Natural Language Processing services

[![Build Status](https://travis-ci.org/bothub-it/bothub-nlp-api.svg?branch=master)](https://travis-ci.org/bothub-it/bothub-nlp-api) [![Coverage Status](https://coveralls.io/repos/github/bothub-it/bothub-nlp-api/badge.svg)](https://coveralls.io/github/bothub-it/bothub-nlp-api) ![version 2.2.0](https://img.shields.io/badge/version-2.2.0-blue.svg) [![python 3.6](https://img.shields.io/badge/python-3.6-green.svg)](https://docs.python.org/3.6/whatsnew/changelog.html) [![license AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-red.svg)](https://github.com/udomobi/bothub-nlp/blob/master/LICENSE)

Check the [main Bothub project repository](https://github.com/Ilhasoft/bothub).


## Services

### bothub-nlp-api

## Packages

### [bothub-backend](https://github.com/bothub-it/bothub-backend) (python 3.6)

### [bothub-nlp-celery](https://github.com/bothub-it/bothub-nlp-celery) (python 3.6)


# Requirements

* Python (3.6)
* Docker
* Docker-Compose

## Development

Use ```make``` commands to ```init_development_env```.

| Command | Description |
|--|--|
| make init_development_env | Init file .env with variables environment

## Environment Variables

### General

| Variable | Type | Default | Description |
|--|--|--|--|
| ENVIRONMENT | `str` | `production` | |
| BOTHUB_ENGINE_URL | `str` | `https://api.bothub.it` | Web service api url |
| BOTHUB_NLP_API_HOST | `str` | `0.0.0.0` | Web service ip |
| BOTHUB_NLP_API_PORT | `int` | `2657` | Web service port |
| BOTHUB_NLP_API_WEB_CONCURRENCY | `int` | `None` |  |
| BOTHUB_NLP_API_WORKERS_PER_CORE | `int` | `3` |  |
| BOTHUB_NLP_API_LOG_LEVEL | `str` | `info` |  |
| BOTHUB_NLP_API_KEEPALIVE | `int` | `120` |  |
| BOTHUB_NLP_SENTRY_CLIENT | `bool` | `False` | Enable Sentry Client |
| BOTHUB_NLP_SENTRY | `str` | `None` | Sentry Client URL |
| SUPPORTED_LANGUAGES | `str` | `en|pt` | Set supported languages. Separate languages using `|` |

### QA tasks

| Variable | Type | Default | Description |
|--|--|--|--|
| BOTHUB_NLP_API_ENABLE_QA_ROUTE | `bool` | `False` | Enable QA api route |
| BOTHUB_NLP_API_QA_TEXT_LIMIT | `int` | `25000` | Limit of characters allowed in QA text |
| BOTHUB_NLP_API_QA_QUESTION_LIMIT | `int` | `500` | Limit of characters allowed in QA question |


### Training

| Variable | Type | Default | Description |
|--|--|--|--|
| BOTHUB_SERVICE_TRAIN | `str` | `celery` | `celery` to train on celery worker or `ai-platform` to use GCP service |
| BOTHUB_GOOGLE_PROJECT_ID | `int` | `None` | GCP project id |
| BOTHUB_GOOGLE_CREDENTIALS_REFRESH_TOKEN | `str` | `None` | GCP credentials |
| BOTHUB_GOOGLE_CREDENTIALS_TOKEN_URI | `str` | `None` | GCP credentials |
| BOTHUB_GOOGLE_CREDENTIALS_CLIENT_ID | `str` | `None` | GCP credentials |
| BOTHUB_GOOGLE_CREDENTIALS_CLIENT_SECRET | `str` | `None` | GCP credentials |
| BOTHUB_GOOGLE_AI_PLATFORM_REGISTRY | `str` | `us.gcr.io/bothub/bothub-nlp-ai-platform` | Google Container Registry (GCR) project url |
| BOTHUB_GOOGLE_AI_PLATFORM_IMAGE_VERSION | `str` | `1.0.0` | String to match built image version in google GCR |
| BOTHUB_GOOGLE_AI_PLATFORM_PACKAGE_URI | `list` | `["gs://poc-training-ai-platform/bothub-nlp-ai-platform/bothub-nlp-ai-platform-0.1.tar.gz"]` |  |
| BOTHUB_GOOGLE_AI_PLATFORM_JOB_TIMEOUT | `int` | `None` | Time limit (seconds) a job can run before sending a cancel signal to GCP |

### Celery connection
Needed variables to connect to celery running on workers

| Variable | Type | Default | Description |
|--|--|--|--|
| BOTHUB_NLP_CELERY_BROKER_URL | `str` | `redis://localhost:6379/0	` | `Celery Broker URL, check usage instructions in Celery Docs` |
| BOTHUB_NLP_CELERY_BACKEND_URL | `str` | `BOTHUB_NLP_CELERY_BROKER_URL` value | Celery Backend URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |

### Celery queue
Variables to set available queues running on workers

| Variable | Type | Default | Description |
|--|--|--|--|
| AVAILABLE_SPACY_MODELS | `string` | <code>en&#124;pt_br&#124;es&#124;fr&#124;ru</code> | Available SPACY models of working nodes |
| AVAILABLE_BERT_MODELS | `string` | <code>en&#124;pt_br&#124;xx</code> | Available BERT models of working nodes |
| AVAILABLE_QA_MODELS | `string` | <code>en&#124;pt_br&#124;xx</code> | Available QA models of working nodes |
| AVAILABLE_SPECIFIC_SPACY_QUEUES | `string` | <code>en&#124;pt_br&#124;es&#124;fr&#124;ru</code> | Available languages with word2vec models. It means there is workers listening to `en-SPACY, pt_br-SPACY, ...` queues |
| AVAILABLE_SPECIFIC_BERT_QUEUES | `string` | <code>en&#124;pt_br</code> | Available languages with BERT models. It means there is workers listening to `en-BERT, pt_br-BERT` queues. Other languages will be sent to `multilang-BERT` queue |
| AVAILABLE_SPECIFIC_QA_QUEUES | `string` | <code>en&#124;pt_br</code> | Available languages with QA models. It means there is workers listening to `en-QA, pt_br-QA` queues. Other languages will be sent to `multilang-QA` queue |
| AVAILABLE_SPECIFIC_QUEUES | `string` | `""` | Languages without model that need to be handled in exclusive queues. It means there is workers listening to `""` queue. Other languages will be sent to `multilang` queue |
