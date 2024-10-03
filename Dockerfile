# syntax=docker/dockerfile:1


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
    gnupg

RUN echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /etc/apt/trusted.gpg.d/google-chrome.gpg
RUN apt-get update && apt-get install google-chrome-stable=* -y


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


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


RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


USER appuser

COPY --chown=appuser:appuser --chmod=755 . .


EXPOSE 8000


RUN Xvfb :99 -screen 0 1600x900x24 > /dev/null 2>&1 & \
    export DISPLAY=:99

CMD ["fastapi", "run", "main.py", "--port", "8000"]