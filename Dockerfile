FROM python:3.11-slim

WORKDIR /code
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code, Alembic, and consumer
COPY ./app /code/app
COPY ./alembic.ini /code/
COPY ./alembic /code/alembic

# Default command: run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
