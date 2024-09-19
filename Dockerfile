FROM python:3.12-slim


RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install poetry

RUN poetry install --no-root

COPY . /app

EXPOSE 3000


CMD ["python", "main.py"]