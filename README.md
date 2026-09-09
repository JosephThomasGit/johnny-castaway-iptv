# Johnny Castaway IPTV Streamer

Bring the legendary 1992 Sierra On-Line screensaver into your modern home server ecosystem. This project provides a fully automated, containerized pipeline that takes your locally supplied legacy Windows installer or extracted assets, executes them headlessly inside a secure 32-bit Wine and X11 graphics stack, and transcodes the output into a real-time, low-latency HLS (`.m3u8`) IPTV stream. 

Whether you want a nostalgic background feed running 24/7 on a custom IPTV channel, a unique dashboard element, or an entertaining addition to your media server lineup, this container bridges a 16-bit classic directly into modern streaming architectures.

## Architecture & How It Works

Running a 32-bit/16-bit Windows application on a modern Linux-based container requires a specialized compatibility layer. When you launch the container, the internal orchestrator script executes a structured multi-stage initialization:

1. **Asset Processing:** Scans your locally mounted file path, automatically determining whether to unpack an Inno Setup installer (`.exe`), extract a `.zip` archive, or ingest raw `.scr` and `.dat` files directly into a secure workspace.
2. **Headless Display Provisioning:** Boots an isolated virtual X11 framebuffer (`Xvfb`) configured at an 800x600 resolution with 24-bit color depth, removing any requirement for physical display hardware or host GPU access.
3. **Window Management & Scaling:** Spawns a lightweight window manager (`Fluxbox`) alongside Wine (`wine32`), then utilizes window utility automation (`xdotool`) to dynamically resize and anchor the screensaver interface cleanly to the full virtual viewport, preventing letterboxing and resolution-change exceptions.
4. **Live Transcoding:** Engaged instances of FFmpeg capture the virtual display buffer (`x11grab`) in real-time, encoding the stream using `libx264` with a rolling HLS segment configuration (`.ts` files accompanied by a `.m3u8` playlist) designed to prevent storage bloat.
5. **HTTP Delivery:** Exposes a lightweight built-in Python web server to broadcast the HLS stream reliably across your local network.

## Key Features

* **Bring Your Own File (BYOF):** Completely decoupled from fragile online hotlinks or copyrighted binary distribution. You maintain your own files locally and pass them securely via container volumes.
* **Headless Linux Compatibility:** Fully bundles `wine32`, `Xvfb`, `Fluxbox`, and `xdotool` into a unified Debian-slim image, ensuring consistent execution across Windows, macOS, and Linux via Docker Desktop.
* **Automated Window Management:** Bypasses legacy resolution-change crashes and display scaling bugs by programmatically forcing the application to occupy the correct screen parameters.
* **Resource Guardrails:** Includes built-in resource constraints (`deploy.resources.limits`) to ensure memory and CPU spikes remain safely capped during continuous 24/7 operation.

## System Requirements & Footprint

* **Docker Desktop / Engine:** Running and accessible on your host system.
* **Storage Footprint:** Approximately **1.2 GB** for the Docker image (driven by the Wine compatibility layer and X11 graphics libraries).
* **Memory Usage:** Consumes roughly **400 MB to 600 MB of RAM** while actively transcoding.

---

## Installation & Setup Guide

### 1. Clone the Repository
Open your terminal and clone the repository to your local machine:
```bash
git clone [https://github.com/YourUsername/johnny-castaway-iptv.git](https://github.com/YourUsername/johnny-castaway-iptv.git)
cd johnny-castaway-iptv


Disclaimer
This repository contains strictly independent, open-source automation scripts, configuration templates, and orchestration files designed to run legacy software environments within modern containerized infrastructure. This project does not distribute, host, bundle, or share copyrighted software binaries, proprietary installers, or commercial assets.

All intellectual property rights, trademarks, and copyrights associated with Johnny Castaway remain the exclusive property of their respective creators, developers, and copyright holders.
