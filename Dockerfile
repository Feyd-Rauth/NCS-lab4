FROM python:3.10-alpine AS builder

WORKDIR /app
ADD pyproject.toml poetry.lock /app/

RUN apk add build-base libffi-dev
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
RUN poetry install --no-ansi


FROM python:3.10-alpine
WORKDIR /app
ARG FOLDER

COPY --from=builder /app /app
ADD "$FOLDER" /app

CMD /app/.venv/bin/python -m main
