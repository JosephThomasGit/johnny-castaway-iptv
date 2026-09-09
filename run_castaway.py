print("Starting Virtual Display (Xvfb)...")
subprocess.Popen(['Xvfb', ':99', '-screen', '0', '800x600x24'])
time.sleep(2)
os.environ['DISPLAY'] = ':99'

print("Starting Window Manager (Fluxbox)...")
subprocess.Popen(['fluxbox'])
time.sleep(1)

# Configure Wine via registry to block screensavers from altering display settings
print("Configuring Wine display settings...")
reg_cmd = [
    'wine', 'reg', 'add', 
    'HKEY_CURRENT_USER\\Software\\Wine\\AppDefaults\\SCRCAST.SCR\\X11 Driver', 
    '/v', 'UseXVidMode', '/t', 'REG_SZ', '/d', 'N', '/f'
]
subprocess.run(reg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Alternative fallback global registry key to disable resolution changes
reg_global = [
    'wine', 'reg', 'add', 
    'HKEY_CURRENT_USER\\Software\\Wine\\Graphics', 
    '/v', 'UseXVidMode', '/t', 'REG_SZ', '/d', 'N', '/f'
]
subprocess.run(reg_global, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"Booting Johnny Castaway from {scr_file}...")
subprocess.Popen(['wine', scr_file, '/S'], cwd=scr_work_dir)

# Give Wine a moment to spawn the window, then force it to scale to full 800x600
time.sleep(3)
try:
    subprocess.run(['xdotool', 'search', '--onlyvisible', '--class', 'wine', 'windowsize', '800', '600'], check=False)
    subprocess.run(['xdotool', 'search', '--onlyvisible', '--class', 'wine', 'windowmove', '0', '0'], check=False)
except Exception as e:
    print(f"Window sizing note: {e}")

print("Starting FFmpeg HLS Transcoder...")
