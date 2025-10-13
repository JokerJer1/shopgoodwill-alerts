#!/usr/bin/env python3

import json
from shopgoodwill import Shopgoodwill


def get_access_token(username, password):
    """Get access token by logging in with username/password"""
    auth_info = {
        "username": username,
        "password": password
    }
    
    sgw = Shopgoodwill(auth_info)
    
    # The token is stored in the session headers
    auth_header = sgw.shopgoodwill_session.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        print(f"Access Token: {token}")
        
        # Save to config
        config = {
            "auth_info": {
                "access_token": token,
                "username": username,
                "password": password
            }
        }
        
        with open('feed_config.json', 'w') as f:
            json.dump(config, f, indent=4)
        
        print("Token saved to feed_config.json")
        return token
    else:
        print("Failed to get access token")
        return None

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python get_token.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    get_access_token(username, password)
