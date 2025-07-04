FROM python:3.10-slim

WORKDIR /app

ENV LOG_FILE=/app/app.log

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN apt-get update && apt-get install -y cron


COPY app/ .

COPY logger_config.py /app/logger_config.py

ENV PYTHONPATH=/app

COPY app/crontab.txt /etc/cron.d/parse-cron
COPY .env /app/.env

RUN chmod 0644 /etc/cron.d/parse-cron

RUN crontab /etc/cron.d/parse-cron

RUN touch /app/app.log

CMD ["sh", "-c", "python main.py && cron -f & tail -f /app/app.log"]