FROM python:3.10-slim

ENV WORKDIR /home/app
ENV BOTHUB_NLP_API_PORT 2657
WORKDIR $WORKDIR

RUN apt-get update \
 && apt-get install --no-install-recommends --no-install-suggests -y apt-utils \
 && apt-get install --no-install-recommends --no-install-suggests -y gcc bzip2 git curl nginx libpq-dev gettext \
    libgdal-dev python3-cffi python3-gdal vim

RUN pip install -U pip==21.3.1 setuptools
RUN pip install pipenv==2023.6.2
RUN pip install gunicorn==19.9.0
RUN apt-get install -y libjpeg-dev libgpgme-dev linux-libc-dev musl-dev libffi-dev libssl-dev
ENV LIBRARY_PATH=/lib:/usr/lib

COPY . .

RUN pipenv install --system

RUN chmod +x ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]
