# syntax=docker/dockerfile:1.4
FROM debian:bookworm-slim

RUN dpkg --add-architecture i386 && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    xvfb \
    wine \
    wine32 \
    pulseaudio \
    alsa-utils \
    ffmpeg \
    python3 \
    innoextract \
    p7zip-full \
    unzip \
    xdotool \
    && rm -rf /var/lib/apt/lists/*

ENV WINEDEBUG=-all
ENV WINEARCH=win32

WORKDIR /app

COPY <<-'PYTHON_EOF' /app/run_castaway.py
