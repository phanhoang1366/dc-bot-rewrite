FROM python:3.10-alpine

ADD . /app
WORKDIR /app
RUN apk add --update --no-cache ffmpeg && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    apk del build-base --purge

ENTRYPOINT python3 /app/bot.py
