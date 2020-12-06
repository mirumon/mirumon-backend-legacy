FROM python:3.8.6-slim-buster

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION 1.1.3
ENV POETRY_GET_URL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py

RUN apt-get update && \
    apt-get install -y curl

# Create app directory for poetry packages. Required for running `poetry install`
WORKDIR /mirumon
RUN touch ./__init__.py && \
    curl -sSL "$POETRY_GET_URL" | python
# Run to configure current shell run. It is same as `source $HOME/.poetry/env`
ENV PATH="${PATH}:/root/.poetry/bin"


# Install deps
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-dev

# Copy code
COPY . .

EXPOSE 8000

# Run migrations and start server
CMD poetry run alembic upgrade head && \
    poetry run scripts/runserver
