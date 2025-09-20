FROM python:3.9-slim

WORKDIR /app

COPY analytics/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY analytics/ .
COPY utils/ ./utils/

CMD ["python", "app.py"]