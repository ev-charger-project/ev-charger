FROM python:3.10-buster AS builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /code

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

FROM python:3.10-slim-buster AS runtime
RUN apt-get update && apt-get install libpq5 -y

ENV VIRTUAL_ENV=/code/.venv \
    PATH="/code/.venv/bin:$PATH" \
    VENV_PATH="/opt/pysetup/.venv"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

WORKDIR /code

COPY alembic.ini /code/
COPY ./app /code/app
COPY ./migrations /code/migrations

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


EXPOSE 4000

CMD ["sh", "-c", "alembic upgrade head && uvicorn --host=0.0.0.0 --port=4000 app.main:app"]
