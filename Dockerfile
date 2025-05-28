FROM python:3.12-slim-bullseye

ENV PYTHONPATH=/

COPY pyproject.toml /
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY ./app /app

ENTRYPOINT ["sh", "-c", "poetry run alembic -c /app/db/alembic.ini upgrade head && uvicorn app.__main__:app --host 0.0.0.0 --port 5000"]
