FROM python:3.11-slim

WORKDIR /code
ENV PYTHONUNBUFFERED=1

# Install build tools for psycopg2 and other C extensions
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc build-essential \
  && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code, Alembic, and consumer
COPY ./app /code/app
COPY ./consumers /code/consumers
COPY ./alembic.ini /code/
COPY ./alembic /code/alembic

# Default command: run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
