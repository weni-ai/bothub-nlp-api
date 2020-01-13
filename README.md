# Bothub NLP - Natural Language Processing services

[![Build Status](https://travis-ci.org/bothub-it/bothub-nlp-api.svg?branch=master)](https://travis-ci.org/bothub-it/bothub-nlp-api) [![Coverage Status](https://coveralls.io/repos/github/bothub-it/bothub-nlp-api/badge.svg)](https://coveralls.io/github/bothub-it/bothub-nlp-api) ![version 2.2.0](https://img.shields.io/badge/version-2.2.0-blue.svg) [![python 3.6](https://img.shields.io/badge/python-3.6-green.svg)](https://docs.python.org/3.6/whatsnew/changelog.html) [![license AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-red.svg)](https://github.com/udomobi/bothub-nlp/blob/master/LICENSE)

Check the [main Bothub project repository](https://github.com/Ilhasoft/bothub).


## Services

### bothub-nlp-api

## Packages

### bothub-nlp (python 3.6)

### bothub-nlp-celery (python 3.6)


# Requirements

* Python (3.6)
* Docker
* Docker-Compose

## Development

Use ```make``` commands to ```lint```, ```init_env```, ```start_development```.

| Command | Description |
|--|--|
| make lint | Show lint warnings and errors
| make init_env | Init file .env with variables environment
| make start_development | Create .env with variable environment and start build docker

## Environment Variables

| Variable | Type | Default | Description |
|--|--|--|--|
| ENVIRONMENT | `str` | `production` |  |
| BOTHUB_NLP_API_HOST | `str` | `0.0.0.0` | Web service ip |
| BOTHUB_NLP_API_PORT | `int` | `2657` | Web service port |
| BOTHUB_NLP_SENTRY_CLIENT | `bool` | `None` | Enable Sentry Client |
| BOTHUB_NLP_SENTRY | `str` | `None` | Sentry Client URL |
| SUPPORTED_LANGUAGES | `str` | `en|pt` | Set supported languages. Separe languages using |. You can set location follow the format: [LANGUAGE_CODE]:[LANGUAGE_LOCATION]. |
| BOTHUB_ENGINE_URL | `str` | `https://api.bothub.it` | Web service url |
| BOTHUB_NLP_CELERY_BROKER_URL | `str` | `redis://localhost:6379/0	` | `Celery Broker URL, check usage instructions in Celery Docs` |
| BOTHUB_NLP_CELERY_BACKEND_URL | `str` | `BOTHUB_NLP_CELERY_BROKER_URL` value | Celery Backend URL, check usage instructions in [Celery Docs](http://docs.celeryproject.org/en/latest/index.html) |
| BOTHUB_NLP_NLU_AGROUP_LANGUAGE_QUEUE | `boolean` | `True` | Agroup tasks by language in celery queue, if `True` there will be only one queue per language. |
| BOTHUB_NLP_API_WORKERS_PER_CORE | `int` | `3` |  |
| BOTHUB_NLP_API_WEB_CONCURRENCY | `int` | `None` |  |
| BOTHUB_NLP_API_LOG_LEVEL | `str` | `info` |  |
| BOTHUB_NLP_API_KEEPALIVE | `int` | `120` |  |
