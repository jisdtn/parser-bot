FROM python:3.10-slim

WORKDIR /app

COPY bot/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY bot/ .

COPY logger_config.py /app/logger_config.py

ENV PYTHONPATH=/app

CMD ["python", "bot.py"]
