#!/bin/sh
# cron jobs don't inherit the container's environment, so the variables
# passed in via `env_file`/`-e` are dumped to a .env file on the writable
# container layer (never baked into the image) for python-dotenv to read.
set -e

env | grep -E '^(BOT_TOKEN|DATABASE_URL|LOG_FILE)=' > /app/.env
chmod 600 /app/.env

python main.py
cron -f &
tail -f /app/app.log
