FROM python:3.7.4

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .

# for installing application from poetry
RUN mkdir app && touch ./app/__init__.py && \
    pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev

COPY . .

CMD alembic upgrade head && uvicorn --host 0.0.0.0 app.main:app
