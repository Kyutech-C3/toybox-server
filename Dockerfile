FROM python:3.9-alpine

RUN mkdir /api

WORKDIR /api

RUN apk add musl-dev gcc make g++ file

RUN apk add --no-cache postgresql-libs && \
	apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

RUN pip install pipenv

COPY ./Pipfile .
COPY ./Pipfile.lock .

RUN pipenv install