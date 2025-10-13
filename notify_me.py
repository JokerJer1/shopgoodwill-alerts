#!/usr/bin/env python3

import subprocess
import json
import os
from datetime import datetime

def send_notification(message):
    """Send notification using system notification"""
    try:
        # For Linux/WSL
        subprocess.run(['notify-send', 'ShopGoodwill Alert', message])
    except:
        print(f"NOTIFICATION: {message}")

def run_and_notify():
    """Run the alert script and notify on new items"""
    print(f"Running ShopGoodwill alerts at {datetime.now()}")
    
    # Run the alert script
    result = subprocess.run(['python', 'alert_on_new_query_results.py', '--all'], 
                          capture_output=True, text=True)
    
    # Check if new items were found
    if "Found" in result.stdout and "new items" in result.stdout:
        # Extract the number of new items
        lines = result.stdout.split('\n')
        for line in lines:
            if "Found" in line and "new items" in line:
                send_notification(line.strip())
                break
    
    print("Alert check completed")

if __name__ == "__main__":
    run_and_notify()
