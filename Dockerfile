FROM python:3.9-alpine

RUN mkdir /api

WORKDIR /api

RUN apk add musl-dev gcc make g++ file

RUN apk add --no-cache postgresql-libs && \
	apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip install --upgrade pip
RUN pip install pipenv
RUN pip install cryptography

COPY ./Pipfile .
COPY ./Pipfile.lock .

RUN pipenv install