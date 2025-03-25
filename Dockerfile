# syntax=docker/dockerfile:1
# Нужно внедрить поддержку .env, адекватное развёртывание через compose 

ARG PYTHON_VERSION=3.12.4
FROM python:${PYTHON_VERSION}-slim as base

RUN apt-get update && apt-get install -y \
    xvfb \
    fluxbox \
    x11vnc \
    x11-apps \  
    sudo \
    wget \
    curl \
    htop \
    gnupg \
    unzip

RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/google-chrome.gpg
RUN apt-get update && apt-get install -y google-chrome-stable
RUN LATEST_CHROME_DRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) \
    && CHROME_DRIVER_URL="https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$LATEST_CHROME_DRIVER_VERSION/linux64/chromedriver-linux64.zip" \
    && wget -O /tmp/chromedriver.zip $CHROME_DRIVER_URL \
    && unzip /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver-linux64 /tmp/chromedriver.zip

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false


ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

RUN mkdir -p /app
RUN chown appuser:appuser /app
WORKDIR /app

RUN pip install poetry
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./
RUN poetry install --no-root

USER appuser
COPY --chown=appuser:appuser --chmod=755 . .

COPY --chown=appuser:appuser .env /app/.env
RUN chmod 600 /app/.env

EXPOSE 8000

RUN Xvfb :99 -screen 0 1600x900x24 > /dev/null 2>&1 & \
    export DISPLAY=:99

CMD ["fastapi", "run", "app/api/main.py", "--port", "8000", "--host", "localhost"]