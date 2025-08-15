FROM python:3.14.0rc1-alpine

ADD . /app
WORKDIR /app
RUN apk add --update --no-cache build-base ffmpeg && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    apk del build-base --purge

ENTRYPOINT python3 /app/bot.py
