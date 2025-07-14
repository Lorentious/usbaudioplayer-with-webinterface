import os
import re
import time
import threading

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame.pkgdata")

import pygame
from flask import Flask, render_template, jsonify, request, send_from_directory, abort
from waitress import serve

def clear_terminal():
    os.system("cls")

def banner():
    print("==============================================")
    print("         Welcome to Remote Audio Player         ")
    print("      powered by Flask, pygame & Waitress     ")
    print("==============================================\n")

clear_terminal()
banner()

app = Flask(__name__)

selected_usb = None
current_file = None

output = os.popen('ipconfig | findstr /i "ipv4"').read()
ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', output)

audio_state = {
    "filename": None,
    "start_time": 0,
    "seek_offset": 0,
    "is_playing": False,
    "duration": 0
}

def list_usb_drives():
    import ctypes
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in range(65, 91):
        if bitmask & 1:
            drive = f"{chr(letter)}:\\"
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
            if drive_type == 2:  # DRIVE_REMOVABLE
                drives.append(drive)
        bitmask >>= 1
    return drives

def list_audio_files(path):
    exts = ['.mp3', '.wav', '.ogg']
    try:
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1].lower() in exts]
    except Exception:
        files = []
    return files

def get_audio_length(path):
    try:
        from mutagen.mp3 import MP3
        from mutagen.oggvorbis import OggVorbis
        from mutagen.wave import WAVE
        ext = os.path.splitext(path)[1].lower()
        if ext == '.mp3':
            audio = MP3(path)
            return audio.info.length
        elif ext == '.ogg':
            audio = OggVorbis(path)
            return audio.info.length
        elif ext == '.wav':
            audio = WAVE(path)
            return audio.info.length
    except Exception:
        pass
    return 0

@app.route('/')
def index():
    files = list_audio_files(selected_usb) if selected_usb else []
    return render_template('index.html', files=files)

@app.route('/stream/<path:filename>')
def stream_file(filename):
    if not selected_usb:
        abort(404)
    if filename not in list_audio_files(selected_usb):
        abort(404)
    return send_from_directory(selected_usb, filename)

@app.route('/play', methods=['POST'])
def play():
    global current_file
    filename = request.json.get("filename")
    path = os.path.join(selected_usb, filename)
    if not os.path.exists(path):
        return jsonify(success=False), 404
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    audio_state.update({
        "filename": filename,
        "duration": get_audio_length(path),
        "start_time": time.time(),
        "seek_offset": 0,
        "is_playing": True
    })
    current_file = filename
    return jsonify(success=True)

@app.route('/stop', methods=['POST'])
def stop():
    pygame.mixer.music.stop()
    audio_state.update({
        "start_time": 0,
        "seek_offset": 0,
        "is_playing": False,
        "filename": None,
        "duration": 0
    })
    return jsonify(success=True)

@app.route('/toggle', methods=['POST'])
def toggle():
    if audio_state["is_playing"]:
        pygame.mixer.music.pause()
        elapsed = time.time() - audio_state["start_time"]
        audio_state["seek_offset"] += elapsed
        audio_state["is_playing"] = False
    else:
        pygame.mixer.music.unpause()
        audio_state["start_time"] = time.time()
        audio_state["is_playing"] = True
    return jsonify(success=True)

@app.route('/seek', methods=['POST'])
def seek():
    seconds = request.json.get('seconds', 0)
    if audio_state["filename"]:
        path = os.path.join(selected_usb, audio_state["filename"])
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(start=seconds)
        audio_state.update({
            "seek_offset": seconds,
            "start_time": time.time(),
            "is_playing": True
        })
    return jsonify(success=True)

@app.route('/status')
def status():
    if audio_state["is_playing"]:
        elapsed = time.time() - audio_state["start_time"]
        position = audio_state["seek_offset"] + elapsed
    else:
        position = audio_state["seek_offset"]
    position = min(position, audio_state["duration"])
    return jsonify({
        "filename": audio_state["filename"],
        "duration": audio_state["duration"],
        "position": position,
        "is_playing": audio_state["is_playing"]
    })

def run_flask():
    print("Flask server is running.")
    print("Listening on: http://localhost:8080")
    for x in ips:
        print(f"Accessible via: http://{x}:8080 (LAN)")
    print("\n")
    print("Press Ctrl+C to stop the server.")
    serve(app, host="0.0.0.0", port=8080)
    

if __name__ == "__main__":
    selected_usb = None
    drives = list_usb_drives()
    if not drives:
        print("No USB drives found.")
        exit(1)
    if len(drives) == 1:
        selected_usb = drives[0]
    else:
        print("Detected USB drives:")
        for i, d in enumerate(drives, 1):
            print(f"{i}. {d}")
        while True:
            choice = input(f"Select USB drive (1-{len(drives)}): ")
            if choice.isdigit() and 1 <= int(choice) <= len(drives):
                selected_usb = drives[int(choice) - 1]
                break
            print("Invalid input. Please try again.")

    print(f"Selected USB drive: {selected_usb}\n")
    pygame.mixer.init()
    threading.Thread(target=run_flask).start()
