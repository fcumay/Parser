
FROM python:3.10-slim-buster
ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN pip install pipenv

WORKDIR /app

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --deploy --ignore-pipfile
COPY main.py .
EXPOSE 8000


CMD ["pipenv", "run", "uvicorn", "main:container_app.app", "--host", "0.0.0.0"]

