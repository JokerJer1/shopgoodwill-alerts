#!/usr/bin/env python3

import os
import sys
import json
from feed_system import FeedSystem, app

def main():
    # Check if config file exists
    config_file = 'feed_config.json'
    if not os.path.exists(config_file):
        print(f"Config file {config_file} not found. Please create it with your ShopGoodwill credentials.")
        print("Example:")
        print(json.dumps({
            "auth_info": {
                "username": "your_username",
                "password": "your_password"
            }
        }, indent=2))
        sys.exit(1)
    
    # Load config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Check if auth info is provided
    auth_info = config.get('auth_info', {})
    if not auth_info.get('username') and not auth_info.get('access_token'):
        print("Please configure your ShopGoodwill credentials in feed_config.json")
        sys.exit(1)
    
    # Start the web server
    web_config = config.get('web_interface', {})
    host = web_config.get('host', '0.0.0.0')
    port = web_config.get('port', 5000)
    debug = web_config.get('debug', True)
    
    print(f"Starting ShopGoodwill Feed System on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()
