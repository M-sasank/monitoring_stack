FROM python:3.9-slim

WORKDIR /app

COPY notification/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY notification/ .
COPY utils/ ./utils/

CMD ["python", "app.py"]