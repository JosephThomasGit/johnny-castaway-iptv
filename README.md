# Johnny Castaway IPTV

Run the classic Johnny Castaway screensaver as an HLS stream for playback on any device (Chrome, Firefox, Roku, etc).

## Features

- Runs Johnny Castaway screensaver in Wine container
- Streams video/audio via HLS at 640x480 30fps
- H.264 video codec (libx264) with AAC audio
- Dual-container architecture: streaming engine + audio server
- Resource optimized: 1.5GB RAM, 2.5 CPU cores
- Smooth playback: 6-second HLS segments, no jitter/glitches
- Compatible with Jellyfin, ersatz TV, Roku, and direct HTTP clients

## Requirements

- Docker & Docker Compose
- Johnny Castaway screensaver executable (`johnnycastaway.exe`)
- ~2GB free disk space for stream segments

## Setup

1. Place `johnnycastaway.exe` in your media folder (default: `C:\Users\jthom\Downloads\`)
2. Update paths in `docker-compose.yml` if needed:
   - `C:/Users/jthom/Downloads:/host_media:ro` → your media path
3. Run: `docker compose up -d`
4. Stream available at: `http://localhost:9081/castaway.m3u8`

## Usage

### Direct URL (Browser, Roku, VLC)
