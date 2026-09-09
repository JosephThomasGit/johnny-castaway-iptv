# Johnny Castaway IPTV Streamer

This project brings the legendary 1992 Johnny Castaway screensaver into the modern era. It takes your locally supplied screensaver file, runs it headlessly inside a Docker container via Wine, and broadcasts the video as a lightweight HLS (`.m3u8`) stream. 

## Features
* **Bring Your Own File:** Designed to run with your locally downloaded screensaver installer or extracted assets without committing copyrighted binaries to Git.
* **Headless Emulation:** Uses `Xvfb`, `Fluxbox`, `Wine32`, and `xdotool` to run and scale the 16-bit application cleanly on Linux.
* **Live Transcoding:** FFmpeg captures the virtual display and outputs a rolling HLS stream.
* **Cross-Platform:** Works seamlessly on Windows, Mac, and Linux through Docker Desktop.

> **Note on Image Size:** Because this container bundles a graphical environment and a 32-bit Windows compatibility layer (Wine), the resulting Docker image size is roughly **1.2 GB**, consuming roughly 400-600 MB of RAM while running.

## Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* Git installed on your system.
* A local copy of your screensaver file (e.g., `jc15.exe` or `.scr` assets).

## Installation & Running

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/johnny-castaway-iptv.git](https://github.com/YourUsername/johnny-castaway-iptv.git)
   cd johnny-castaway-iptv
