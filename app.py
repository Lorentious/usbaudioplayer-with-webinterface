import os
import threading
import sounddevice as sd
from flask import Flask, render_template, jsonify, request, send_from_directory, abort

app = Flask(__name__)

selected_usb = None
selected_audio_device = None

def list_usb_drives():
    import ctypes
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in range(65, 91):
        if bitmask & 1:
            drive = f"{chr(letter)}:\\"
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive)
            if drive_type == 2:
                drives.append(drive)
        bitmask >>= 1
    return drives

def list_audio_devices():
    devices = sd.query_devices()
    output_devices = [d for d in devices if d['max_output_channels'] > 0]
    return output_devices

def choose_usb():
    drives = list_usb_drives()
    print("USB-Sticks gefunden:")
    for i, d in enumerate(drives, 1):
        print(f"{i}. {d}")
    if not drives:
        print("Keine USB-Sticks gefunden!")
        return None
    while True:
        choice = input(f"Wähle USB-Stick (1-{len(drives)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(drives):
            return drives[int(choice) - 1]
        print("Ungültige Eingabe!")

def choose_audio_device():
    devices = list_audio_devices()
    print("\nAudio-Ausgabegeräte gefunden:")
    for i, d in enumerate(devices, 1):
        print(f"{i}. {d['name']}")
    while True:
        choice = input(f"Wähle Audio-Gerät (1-{len(devices)}): ")
        if choice.isdigit() and 1 <= int(choice) <= len(devices):
            return devices[int(choice) - 1]
        print("Ungültige Eingabe!")

def list_audio_files(path):
    exts = ['.mp3', '.wav', '.ogg']
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1].lower() in exts]
    return files

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

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    selected_usb = choose_usb()
    selected_audio_device = choose_audio_device()
    print(f"Ausgewählter USB-Stick: {selected_usb}")
    print(f"Ausgewähltes Audio-Gerät: {selected_audio_device['name']}")

    threading.Thread(target=run_flask).start()
