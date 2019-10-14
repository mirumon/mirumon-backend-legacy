FROM python:3.7.4

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .

RUN pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev

COPY . .

CMD uvicorn --host 0.0.0.0 app.main:app
