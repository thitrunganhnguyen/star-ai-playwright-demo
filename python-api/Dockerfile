FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ai_agent.py .
COPY api_server.py .

EXPOSE 8080

CMD ["python3", "api_server.py"]