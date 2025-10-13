#!/usr/bin/env python3

import os
import json

def setup_config():
    """Set up config.json with environment variables for GitHub Actions"""
    
    # Load the template config
    with open('config-github.json', 'r') as f:
        config = json.load(f)
    
    # Replace environment variables
    config['auth_info']['username'] = os.getenv('SHOPGOODWILL_USERNAME', '')
    config['auth_info']['password'] = os.getenv('SHOPGOODWILL_PASSWORD', '')
    config['pushover']['token'] = os.getenv('PUSHOVER_TOKEN', '')
    config['pushover']['user'] = os.getenv('PUSHOVER_USER', '')
    
    # Save the actual config
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("✅ Config set up with environment variables")

if __name__ == "__main__":
    setup_config()
