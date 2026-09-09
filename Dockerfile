FROM debian:bookworm-slim

RUN dpkg --add-architecture i386 && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    xvfb \
    fluxbox \
    wine \
    wine32 \
    ffmpeg \
    python3 \
    wget \
    innoextract \
    p7zip-full \
    && rm -rf /var/lib/apt/lists/*

ENV WINEDEBUG=-all
ENV WINEARCH=win32

WORKDIR /app

COPY run_castaway.py .

EXPOSE 8080

CMD ["python3", "-u", "run_castaway.py"]
