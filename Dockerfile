# syntax=docker/dockerfile:1.4
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
    unzip \
    && rm -rf /var/lib/apt/lists/*

ENV WINEDEBUG=-all
ENV WINEARCH=win32

WORKDIR /app

# Embedded Python orchestrator pointing to a stable mirror source
COPY <<-'EOF' /app/run_castaway.py
import subprocess
import time
import os
import http.server
import socketserver
import urllib.request
import shutil

SS_DIR = '/app/screensaver'
STREAM_DIR = '/app/stream'
# Fallback to a stable archive mirror URL if screensaversplanet throws 404
DOWNLOAD_URL = os.environ.get('DOWNLOAD_URL', 'https://ia801400.us.archive.org/3/items/johnny-castaway-screensaver/johnny-castaway-screensaver.zip')
PORT = 9081

os.makedirs(STREAM_DIR, exist_ok=True)
os.makedirs(SS_DIR, exist_ok=True)

def find_scr_file():
    for root, dirs, files in os.walk(SS_DIR):
        for file in files:
            if file.lower().endswith('.scr'):
                return os.path.join(root, file)
    return None

scr_file = find_scr_file()

if not scr_file:
    print(f"Downloading installer package from: {DOWNLOAD_URL}")
    is_zip = DOWNLOAD_URL.lower().endswith('.zip')
    archive_path = '/app/installer.zip' if is_zip else '/app/installer.exe'
    
    req = urllib.request.Request(DOWNLOAD_URL, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response, open(archive_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        print(f"ERROR: Failed to download archive: {e}")
        exit(1)
        
    print("Download complete. Extracting payload...")
    
    if is_zip:
        subprocess.run(['unzip', '-o', archive_path, '-d', SS_DIR], check=True)
    else:
        result = subprocess.run(['innoextract', '-d', SS_DIR, archive_path])
        if result.returncode != 0:
            print("innoextract fallback to 7zip...")
            subprocess.run(['7z', 'x', archive_path, f'-o{SS_DIR}', '-y'], check=True)
            
    scr_file = find_scr_file()

if not scr_file:
    print("ERROR: Could not locate a valid .SCR file following extraction.")
    exit(1)

work_dir = os.path.dirname(scr_file)

print("Starting Virtual Display (Xvfb)...")
subprocess.Popen(['Xvfb', ':99', '-screen', '0', '800x600x24'])
time.sleep(2)
os.environ['DISPLAY'] = ':99'

print("Starting Window Manager (Fluxbox)...")
subprocess.Popen(['fluxbox'])
time.sleep(1)

print(f"Booting Johnny Castaway from {scr_file}...")
subprocess.Popen(['wine', scr_file, '/S'], cwd=work_dir)

print("Starting FFmpeg HLS Transcoder...")
ffmpeg_cmd = [
    'ffmpeg', '-nostdin', '-y',
    '-video_size', '800x600',
    '-framerate', '30',
    '-f', 'x11grab', '-i', ':99.0',
    '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
    '-f', 'hls', 
    '-hls_time', '4', 
    '-hls_list_size', '5',
    '-hls_flags', 'delete_segments',
    '/app/stream/castaway.m3u8'
]
subprocess.Popen(ffmpeg_cmd)

print(f"Starting HTTP Stream Server on port {PORT}...")
os.chdir(STREAM_DIR)
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()
EOF

EXPOSE 9081
CMD ["python3", "-u", "/app/run_castaway.py"]
