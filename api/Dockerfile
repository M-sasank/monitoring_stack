FROM python:3.9-slim

WORKDIR /app

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ .
COPY utils/ ./utils/

EXPOSE 8080

CMD ["python", "app.py"]