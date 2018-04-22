FROM python:3.6.5-alpine3.7

RUN apk --no-cache add sqlite
RUN mkdir /data

RUN pip install pipenv

WORKDIR /app

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock

RUN pipenv install --deploy --system

COPY . /app
