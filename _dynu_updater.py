# dynu_updater.py

#!/usr/bin/env python3
import os
import json
import requests
import time
from datetime import datetime, timedelta

def update_dynu():
    config_path = "/opt/phantomnet/dynu_config.json"
    with open(config_path, "r") as f:
        config = json.load(f)

    domain = config["domain"]
    token = config["token"]
    last_update = config["last_update"]

    if last_update == "never" or (datetime.now() - datetime.strptime(last_update, '%Y-%m-%d %H:%M:%S')).seconds > 28800:
        try:
            # Get current public IP
            ip_response = requests.get('https://api.ipify.org?format=json')
            current_ip = ip_response.json()['ip']

            # Update Dynu
            update_url = f"https://api.dynu.com/nic/update?hostname={domain}&myip={current_ip}"
            response = requests.get(update_url, headers={'Authorization': f'Token {token}'})

            if response.status_code == 200:
                config["last_update"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                with open(config_path, "w") as f:
                    json.dump(config, f)
                print(f"Dynu updated successfully: {domain} -> {current_ip}")
            else:
                print(f"Dynu update failed: {response.text}")
        except Exception as e:
            print(f"Dynu update error: {e}")

if __name__ == "__main__":
    while True:
        update_dynu()
        time.sleep(28800)  # Check every 8 hours