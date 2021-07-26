FROM python:3.6-alpine

ENV WORKDIR /root/app
ENV BOTHUB_NLP_API_PORT 2657

WORKDIR $WORKDIR

COPY . .

RUN apk update \
    && apk add --virtual .build-dependencies --no-cache \
        alpine-sdk \
        git \
        python3-dev

RUN pip install --upgrade pip \
    && pip install -U pip setuptools \
    && pip install -r requirements.txt --no-deps

RUN apk del .build-dependencies \
    && rm -rf /var/cache/apk/*

RUN chmod +x ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
