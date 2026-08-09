FROM python:3.14.3-alpine

ADD . /app
WORKDIR /app
RUN apk add --update --no-cache build-base libc-dev libxslt-dev libxslt ffmpeg && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    apk del build-base libc-dev libxslt-dev --purge

ENTRYPOINT python3 /app/bot.py
