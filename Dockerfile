FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONWARNINGS="ignore"

COPY . .

CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker","-w", "-4", "--bind", "0.0.0.0:8000"]

