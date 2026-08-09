FROM python:3.11-slim

WORKDIR /app

COPY common /app/common
COPY nodes/s1/backend/api/transport-api /app

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x start.sh

CMD ["./start.sh"]