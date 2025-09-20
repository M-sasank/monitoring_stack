FROM python:3.9-slim

WORKDIR /app

COPY processing/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY processing/ .
COPY utils/ ./utils/

CMD ["python", "app.py"]