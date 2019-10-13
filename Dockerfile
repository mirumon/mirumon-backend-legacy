FROM python:3.7

ENV PYTHONUNBUFFERED 1

WORKDIR /mirumon-backend

COPY poetry.lock /mirumon-backend
COPY pyproject.toml /mirumon-backend

RUN pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev

COPY . .

EXPOSE 8000

CMD uvicorn --host 0.0.0.0 app.main:app


