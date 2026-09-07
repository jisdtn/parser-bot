FROM python:3.10-slim-bookworm

WORKDIR /app

ENV LOG_FILE=/app/app.log

COPY app/requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN apt-get update && apt-get install -y cron

RUN playwright install --with-deps chromium


COPY app/ .

COPY logger_config.py /app/logger_config.py

ENV PYTHONPATH=/app

COPY app/crontab.txt /etc/cron.d/parse-cron
COPY app/docker-entrypoint.sh /app/docker-entrypoint.sh

RUN chmod 0644 /etc/cron.d/parse-cron
RUN chmod 0755 /app/docker-entrypoint.sh

RUN crontab /etc/cron.d/parse-cron

RUN touch /app/app.log

CMD ["/app/docker-entrypoint.sh"]
