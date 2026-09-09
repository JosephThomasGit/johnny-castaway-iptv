# Johnny Castaway IPTV Streamer

This project brings the legendary 1992 Johnny Castaway screensaver into the modern era. It automatically downloads the legacy 16-bit Windows screensaver, runs it headlessly inside a Docker container, and broadcasts the video as a lightweight HLS (`.m3u8`) stream. 

Perfect for 24/7 background streaming on home dashboards, custom IPTV channels, or nostalgic media server feeds.

## Features
* **Zero-Touch Setup:** Automatically downloads and unpacks the installer on the first run.
* **Headless Emulation:** Uses a lightweight virtual display (Xvfb) and 32-bit Wine.
* **Live Transcoding:** FFmpeg captures the virtual screen and serves a rolling HLS playlist.
* **Cross-Platform:** Works seamlessly on Windows, Mac, and Linux via Docker Desktop.
* **Host Accessible:** Uses standard port mapping so media servers (Jellyfin, Plex) running directly on the host machine can easily consume the stream.

## Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running on your machine.
* Git installed on your system.

## Installation via Docker Desktop

1. **Clone the repository**  
   Open your terminal (or Command Prompt/PowerShell) and run:
   ```bash
   git clone [https://github.com/YourUsername/johnny-castaway-iptv.git](https://github.com/YourUsername/johnny-castaway-iptv.git)
   cd johnny-castaway-iptv
