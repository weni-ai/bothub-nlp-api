FROM python:3.6-alpine

ENV WORKDIR /root/app
ENV BOTHUB_NLP_API_PORT 2657

WORKDIR $WORKDIR

COPY . .

RUN apk update \
    && apk add --virtual .build-dependencies --no-cache \
        alpine-sdk \
        git \
        python3-dev \
        build-base \
    && pip install --upgrade pip \
    && pip install -U pip setuptools \
    && pip install pipenv==2021.5.29 redis \
    && pipenv install --system --deploy \
    && apk del .build-dependencies \
    && rm -rf /var/cache/apk/*

RUN chmod +x ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
