# johnny-castaway-iptv

This project brings the legendary 1992 Johnny Castaway screensaver into the modern era. It automatically downloads the legacy 16-bit Windows screensaver, runs it headlessly inside a Docker container, and broadcasts the video as a lightweight HLS (`.m3u8`) stream. 

Perfect for 24/7 background streaming on home dashboards, custom IPTV channels, or nostalgic media server feeds.

## Features
* **Zero-Touch Setup:** Automatically downloads and unpacks the installer on the first run.
* **Headless Emulation:** Uses a lightweight virtual display (Xvfb) and 32-bit Wine.
* **Live Transcoding:** FFmpeg captures the virtual screen and serves a rolling HLS playlist.
* **Small Footprint:** Automatically deletes old video segments to prevent storage bloat.

## Prerequisites
* Docker and Docker Compose (or Docker Desktop)

## Installation & Usage

1. Clone this repository:
   ```bash
   git clone [https://github.com/YourUsername/johnny-castaway-iptv.git](https://github.com/YourUsername/johnny-castaway-iptv.git)
   cd johnny-castaway-iptv
