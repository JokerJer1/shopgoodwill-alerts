#!/usr/bin/env python3

import json
import subprocess
import requests
import sys
from datetime import datetime

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
            print(f"✅ Pushover notification sent: {title}")
            return True
        else:
            print(f"❌ Failed to send Pushover notification: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

def run_alerts_and_notify():
    """Run alerts and send notifications for new items"""
    print(f"Running ShopGoodwill alerts at {datetime.now()}")
    
    # Run the alert script
    result = subprocess.run(['python', 'alert_on_new_query_results.py', '--all'], 
                          capture_output=True, text=True)
    
    # Check if there were any new items found
    if result.returncode == 0 and result.stdout:
        lines = result.stdout.strip().split('\n')
        new_items_found = False
        
        for line in lines:
            if "Found" in line and "new items" in line:
                new_items_found = True
                # Extract the number and query name
                parts = line.split()
                if len(parts) >= 3:
                    count = parts[1]
                    query_name = " ".join(parts[3:]) if len(parts) > 3 else "Search"
                    
                    message = f"Found {count} new items in {query_name}!"
                    send_pushover_notification(message, "New ShopGoodwill Items!")
                break
        
        if not new_items_found:
            print("No new items found in this run")
    else:
        print(f"Alert script failed with return code: {result.returncode}")
        if result.stderr:
            print(f"Error: {result.stderr}")

if __name__ == "__main__":
    run_alerts_and_notify()
