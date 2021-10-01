FROM python:3.9.3-slim-buster

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION 1.1.4
ENV POETRY_GET_URL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl git \
      libpq-dev libc-dev postgresql gcc make

WORKDIR /mirumon-backend

# Poetry provides a custom installer that will install poetry isolated
# from the rest of your system by vendorizing its dependencies.
# This is the recommended way of installing poetry.
# See https://python-poetry.org/docs/#installation
# Run to configure current shell run. It is same as `source $HOME/.poetry/env`
RUN mkdir ./mirumon/ && touch ./mirumon/__init__.py && \
    curl -sSL "$POETRY_GET_URL" | python
ENV PATH="${PATH}:/root/.poetry/bin"

COPY poetry.lock pyproject.toml ./
RUN  poetry install --no-dev

COPY . .

EXPOSE 8000

CMD poetry run alembic upgrade head && \
    poetry run scripts/runserver
