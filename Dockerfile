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
import subprocess
import time
import os
import http.server
import socketserver

WORK_DIR = '/app/extracted'
STREAM_DIR = '/app/stream'
SRC_PATH = os.environ.get('SCR_PATH')
PORT = 9081

os.makedirs(STREAM_DIR, exist_ok=True)
os.makedirs(WORK_DIR, exist_ok=True)

if not SRC_PATH or not os.path.exists(SRC_PATH):
    print(f"ERROR: SCR_PATH environment variable is not set or file does not exist: {SRC_PATH}")
    exit(1)

def find_scr_file():
    for root, dirs, files in os.walk(WORK_DIR):
        for file in files:
            if file.lower().endswith('.scr'):
                return os.path.join(root, file)
    return None

print(f"Processing source file: {SRC_PATH}")
if SRC_PATH.lower().endswith('.exe'):
    result = subprocess.run(['innoextract', '-d', WORK_DIR, SRC_PATH])
    if result.returncode != 0:
        subprocess.run(['7z', 'x', SRC_PATH, f'-o{WORK_DIR}', '-y'])
elif SRC_PATH.lower().endswith('.zip'):
    subprocess.run(['unzip', '-o', SRC_PATH, '-d', WORK_DIR])
elif SRC_PATH.lower().endswith('.scr'):
    dest_path = os.path.join(WORK_DIR, os.path.basename(SRC_PATH))
    import shutil
    shutil.copy(SRC_PATH, dest_path)

scr_file = find_scr_file()

if not scr_file:
    print("ERROR: Could not locate a valid .SCR file from the provided path.")
    exit(1)

scr_work_dir = os.path.dirname(scr_file)

print("Starting PulseAudio sound server...")
subprocess.Popen(['pulseaudio', '--start', '--exit-idle-time=-1'])
time.sleep(2)

print("Starting Virtual Display (Xvfb at 640x480)...")
subprocess.Popen(['Xvfb', ':99', '-screen', '0', '640x480x24'])
time.sleep(2)
os.environ['DISPLAY'] = ':99'

print("Configuring Wine display settings...")
subprocess.run(['wine', 'reg', 'add', 'HKEY_CURRENT_USER\\Software\\Wine\\Graphics', '/v', 'UseXVidMode', '/t', 'REG_SZ', '/d', 'N', '/f'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"Booting Johnny Castaway from {scr_file}...")
subprocess.Popen(['wine', 'explorer', '/desktop=Castaway,640x480', scr_file, '/S'], cwd=scr_work_dir)

time.sleep(4)
try:
    result = subprocess.run(['xdotool', 'search', '--onlyvisible', '--class', 'wine'], capture_output=True, text=True)
    for wid in result.stdout.split():
        wid_clean = wid.strip()
        if wid_clean:
            subprocess.run(['xdotool', 'windowsize', wid_clean, '640', '480'], check=False)
            subprocess.run(['xdotool', 'windowmove', wid_clean, '0', '0'], check=False)
except Exception as e:
    print(f"Window sizing note: {e}")

print("Starting FFmpeg HLS Transcoder (Video + Audio)...")
ffmpeg_cmd = [
    'ffmpeg', '-nostdin', '-y',
    '-f', 'x11grab',
    '-framerate', '20',
    '-video_size', '640x480',
    '-i', ':99.0',
    '-f', 'pulse',
    '-i', 'default.monitor',
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '128k',
    '-ar', '44100',
    '-f', 'hls', 
    '-hls_time', '2', 
    '-hls_list_size', '3',
    '-hls_flags', 'delete_segments',
    '/app/stream/castaway.m3u8'
]
subprocess.Popen(ffmpeg_cmd)

print(f"Starting HTTP Stream Server on port {PORT}...")
os.chdir(STREAM_DIR)
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()
PYTHON_EOF

EXPOSE 9081
CMD ["python3", "-u", "/app/run_castaway.py"]
