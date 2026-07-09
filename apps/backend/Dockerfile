FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace:/workspace/apps/backend:/workspace/apps/backend/app

WORKDIR /workspace/apps/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "apps.backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
