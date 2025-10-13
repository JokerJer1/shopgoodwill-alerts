#!/usr/bin/env python3

import json
import requests

def test_pushover():
    """Test Pushover notification"""
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    pushover_config = config['pushover']
    
    # Pushover API endpoint
    url = "https://api.pushover.net/1/messages.json"
    
    data = {
        "token": pushover_config['token'],
        "user": pushover_config['user'],
        "message": "Test notification from ShopGoodwill script!",
        "title": "Test Alert"
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Pushover test notification sent successfully!")
            print("Check your phone for the notification.")
        else:
            print(f"❌ Failed to send notification: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_pushover()
