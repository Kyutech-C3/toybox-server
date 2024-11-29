FROM python:3.9-alpine

RUN mkdir /api

WORKDIR /api

# timezone
RUN apk update && apk add --no-cache tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime && \
    echo "Asia/Tokyo" > /etc/timezone

# libs
RUN apk add musl-dev gcc make g++ file

# posgresql
RUN apk add --no-cache postgresql-libs && \
	apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libffi-dev

ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip install --upgrade pip
RUN pip install pipenv

COPY ./Pipfile .
COPY ./Pipfile.lock .

RUN pipenv sync
