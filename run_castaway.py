import subprocess
import time
import os
import http.server
import socketserver
import threading

WORK_DIR = '/app/extracted'
STREAM_DIR = '/app/stream'
SRC_PATH = os.environ.get('SCR_PATH')
PORT = 9081

os.makedirs(STREAM_DIR, exist_ok=True)
os.makedirs(WORK_DIR, exist_ok=True)

if not SRC_PATH or not os.path.exists(SRC_PATH):
    print(f"ERROR: SCR_PATH not set or file missing: {SRC_PATH}", flush=True)
    exit(1)

def find_scr_file():
    for root, dirs, files in os.walk(WORK_DIR):
        for file in files:
            if file.lower().endswith('.scr'):
                return os.path.join(root, file)
    return None

print(f"Processing: {SRC_PATH}", flush=True)
if SRC_PATH.lower().endswith('.exe'):
    result = subprocess.run(['innoextract', '-d', WORK_DIR, SRC_PATH], 
                  capture_output=True)
    if result.returncode != 0 or not find_scr_file():
        subprocess.run(['7z', 'x', SRC_PATH, f'-o{WORK_DIR}', '-y'],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

scr_file = find_scr_file()
if not scr_file:
    print("ERROR: No .SCR file found", flush=True)
    exit(1)

scr_work_dir = os.path.dirname(scr_file)

os.environ['WINEPREFIX'] = '/tmp/.wine'
os.environ['WINEARCH'] = 'win32'
os.makedirs('/tmp/.wine', exist_ok=True)

print("Starting Xvfb display server...", flush=True)
xvfb_proc = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '640x480x24'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
os.environ['DISPLAY'] = ':99'

print("Configuring Wine...", flush=True)
subprocess.run(['wine', 'reg', 'add', 'HKEY_CURRENT_USER\\Software\\Wine\\Graphics', 
               '/v', 'UseXVidMode', '/t', 'REG_SZ', '/d', 'N', '/f'],
              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"Launching: {os.path.basename(scr_file)}", flush=True)
wine_proc = subprocess.Popen(['wine', 'explorer', '/desktop=Castaway,640x480', scr_file, '/S'],
                            cwd=scr_work_dir,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)

try:
    result = subprocess.run(['xdotool', 'search', '--onlyvisible', '--class', 'wine'],
                          capture_output=True, text=True, timeout=2)
    for wid in result.stdout.split():
        wid_clean = wid.strip()
        if wid_clean:
            subprocess.run(['xdotool', 'windowsize', wid_clean, '640', '480'],
                          check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(['xdotool', 'windowmove', wid_clean, '0', '0'],
                          check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
except:
    pass

print("Starting PulseAudio for Wine audio capture...", flush=True)
pa_proc = subprocess.Popen(['pulseaudio', '--daemonize=no', '--exit-idle-time=-1'],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

subprocess.run(['wine', 'reg', 'add', 'HKEY_CURRENT_USER\\Software\\Wine\\Drivers',
               '/v', 'Audio', '/t', 'REG_SZ', '/d', 'pulse', '/f'],
              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("Starting audio recorder in background...", flush=True)
audio_file = '/tmp/audio_capture.wav'
arecord_proc = subprocess.Popen(['pacat', '--record', '--format=s16le', '--rate=44100', '--channels=2'],
                               stdout=open(audio_file, 'wb'), stderr=subprocess.DEVNULL)

time.sleep(1)

print("Starting FFmpeg with audio+video...", flush=True)

ffmpeg_cmd = [
    'ffmpeg', '-nostdin', '-y',
    '-f', 'x11grab',
    '-framerate', '30',
    '-video_size', '640x480',
    '-i', ':99.0',
    '-f', 'pulse',
    '-i', 'default',
    '-c:v', 'libx264',
    '-preset', 'medium',
    '-tune', 'zerolatency',
    '-pix_fmt', 'yuv420p',
    '-b:v', '1800k',
    '-maxrate', '2500k',
    '-bufsize', '4000k',
    '-c:a', 'aac',
    '-b:a', '96k',
    '-f', 'hls',
    '-hls_time', '6',
    '-hls_list_size', '8',
    '-hls_flags', 'independent_segments',
    '/app/stream/castaway.m3u8'
]

ffmpeg_proc = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)

def read_ffmpeg():
    try:
        for line in ffmpeg_proc.stderr:
            line_str = line.decode('utf-8', errors='ignore').rstrip()
            if 'error' in line_str.lower():
                print(f"[FFmpeg] {line_str}", flush=True)
    except:
        pass

threading.Thread(target=read_ffmpeg, daemon=True).start()

print("Waiting for stream initialization...", flush=True)
for i in range(30):
    if os.path.exists('/app/stream/castaway.m3u8'):
        print("Stream ready!", flush=True)
        break
    time.sleep(1)

print(f"Starting HTTP server on port {PORT}...", flush=True)
os.chdir(STREAM_DIR)

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
    print(f"Stream: http://localhost:{PORT}/castaway.m3u8", flush=True)
    httpd.serve_forever()
