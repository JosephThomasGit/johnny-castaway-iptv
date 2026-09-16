# Johnny Castaway IPTV

Run the classic Johnny Castaway screensaver as an HLS stream for playback on any device.

## Features

- Runs Johnny Castaway screensaver in Wine
- Streams video/audio via HLS at 640x480 30fps
- H.264 video codec with AAC audio
- Dual-container setup: streaming engine + audio server
- Configurable resource limits (default 1.5GB RAM, 2.5 CPU cores)

## Requirements

- Docker & Docker Compose
- Windows screensaver file: `johnnycastaway.exe`
- ~2GB free disk space for stream segments

## Setup

1. Place `johnnycastaway.exe` in `C:\Users\jthom\Downloads\`
2. Update paths in `docker-compose.yml` as needed
3. Run: `docker compose up -d`
4. Stream available at: `http://localhost:9081/castaway.m3u8`

## Performance Notes

- Jitter/glitches fixed with increased resources and optimized FFmpeg encoding
- Preset: `medium` (good balance of quality/speed)
- Bitrate: 1800k nominal, 2500k max
- Segment time: 6 seconds
- Works on Chrome/Firefox and Roku devices

## Troubleshooting

- Check logs: `docker logs johnny-stream`
- Stream URL returns 404: Wait 30 seconds for FFmpeg to initialize
- No audio: Verify PulseAudio is running in audio-server container
- Jittery playback: Increase memory/CPU limits in docker-compose.yml
