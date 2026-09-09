import subprocess
import time
import os
import http.server
import socketserver
import urllib.request
import shutil

SS_DIR = '/app/screensaver'
STREAM_DIR = '/app/stream'
DOWNLOAD_URL = os.environ.get('DOWNLOAD_URL')

os.makedirs(STREAM_DIR, exist_ok=True)
os.makedirs(SS_DIR, exist_ok=True)

def find_scr_file():
    for root, dirs, files in os.walk(SS_DIR):
        for file in files:
            if file.lower().endswith('.scr'):
                return os.path.join(root, file)
    return None

# 1. Automate Download & Extraction
scr_file = find_scr_file()

if not scr_file:
    if not DOWNLOAD_URL:
        print("ERROR: Screensaver not found and DOWNLOAD_URL is not set.")
        exit(1)
        
    print(f"Downloading installer from {DOWNLOAD_URL}...")
    
    is_zip = DOWNLOAD_URL.lower().endswith('.zip')
    archive_path = '/app/installer.zip' if is_zip else '/app/installer.exe'
    
    req = urllib.request.Request(DOWNLOAD_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(archive_path, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
        
    print("Download complete. Extracting...")
    
    if is_zip:
        subprocess.run(['7z', 'x', archive_path, f'-o{SS_DIR}', '-y'], check=True)
    else:
        print("Attempting to unpack Inno Setup payload...")
        result = subprocess.run(['innoextract', '-d', SS_DIR, archive_path])
        
        if result.returncode != 0:
            print("innoextract failed. Falling back to 7zip...")
            subprocess.run(['7z', 'x', archive_path, f'-o{SS_DIR}', '-y'], check=True)
            
    print("Extraction complete.")
    scr_file = find_scr_file()

if not scr_file:
    print("ERROR: Could not find a .SCR file after extraction.")
    exit(1)

work_dir = os.path.dirname(scr_file)

# 2. Boot the Headless Environment
print("Starting Virtual Display (Xvfb)...")
subprocess.Popen(['Xvfb', ':99', '-screen', '0', '800x600x24'])
time.sleep(2)
os.environ['DISPLAY'] = ':99'

print("Starting Window Manager (Fluxbox)...")
subprocess.Popen(['fluxbox'])
time.sleep(1)

print("Booting Johnny Castaway...")
subprocess.Popen(['wine', scr_file, '/S'], cwd=work_dir)

# 3. Capture and Stream
print("Starting FFmpeg Capture...")
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

print("Starting HTTP Server on port 8080...")
os.chdir(STREAM_DIR)
with socketserver.TCPServer(("", 8080), http.server.SimpleHTTPRequestHandler) as httpd:
    httpd.serve_forever()
