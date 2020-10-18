FROM python:3.8.3

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

WORKDIR /app

# for installing application from poetry
RUN mkdir app && touch ./app/__init__.py && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_VERSION=1.0.10 python
ENV PATH="${PATH}:/root/.poetry/bin"

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install --no-dev

COPY . .

CMD poetry run alembic upgrade head && \
    poetry run uvicorn --host 0.0.0.0 app.main:app
