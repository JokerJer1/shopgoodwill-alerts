#!/usr/bin/env python3

import json
import subprocess
import sys
import requests

def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)

def send_pushover_notification(message, title="ShopGoodwill Alert"):
    """Send notification via Pushover"""
    config = load_config()
    
    if 'pushover' not in config:
        print("Pushover not configured in config.json")
        return
    
    pushover_config = config['pushover']
    
    # Pushover API endpoint
    url = "https://api.pushover.net/1/messages.json"
    
    data = {
        "token": pushover_config['token'],
        "user": pushover_config['user'],
        "message": message,
        "title": title
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"Pushover notification sent: {title}")
        else:
            print(f"Failed to send Pushover notification: {response.text}")
    except Exception as e:
        print(f"Failed to send Pushover notification: {e}")

def run_alerts_with_notifications():
    """Run alerts and send notifications for new items"""
    print("Running ShopGoodwill alerts...")
    
    # Run the alert script
    result = subprocess.run(['python', 'alert_on_new_query_results.py', '--all'], 
                          capture_output=True, text=True)
    
    # Check output for new items
    if result.stdout:
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if "Found" in line and "new items" in line:
                # Extract query name and count
                parts = line.split()
                if len(parts) >= 3:
                    count = parts[1]
                    query = " ".join(parts[3:]) if len(parts) > 3 else "Search"
                    
                    message = f"Found {count} new items in {query}"
                    send_pushover_notification(message, "New ShopGoodwill Items!")
                break
    
    if result.stderr:
        print(f"Errors: {result.stderr}")

if __name__ == "__main__":
    run_alerts_with_notifications()
