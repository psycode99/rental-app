FROM python:3.10-slim-bullseye

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

WORKDIR /api

COPY requirements.txt /api

RUN pip install --no-cache-dir -r requirements.txt

COPY . /api

ENV PYTHONPATH=/api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]