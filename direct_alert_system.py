#!/usr/bin/env python3

import json
import requests
import shopgoodwill
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
        return False
    
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

def load_seen_listings():
    """Load previously seen listings"""
    try:
        with open('seen_listings.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_seen_listings(seen_listings):
    """Save seen listings to file"""
    with open('seen_listings.json', 'w') as f:
        json.dump(seen_listings, f)

def check_for_new_items():
    """Check for new items and send notifications"""
    print(f"Checking for new ShopGoodwill items at {datetime.now()}")
    
    # Load config and create ShopGoodwill instance
    config = load_config()
    auth_info = config['auth_info']
    sgw = shopgoodwill.Shopgoodwill(auth_info)
    
    # Load previously seen items
    seen_listings = load_seen_listings()
    print(f"Previously seen {len(seen_listings)} items")
    
    # Check each query
    total_new_items = 0
    
    for query_name, query_params in config['saved_queries'].items():
        print(f"\nChecking query: {query_name}")
        
        try:
            # Run the search
            results = sgw.get_query_results(query_params)
            print(f"Found {len(results)} total items for '{query_name}'")
            
            # Check for new items
            new_items = []
            for item in results:
                item_id = str(item.get('itemID', ''))
                if item_id and item_id not in seen_listings:
                    new_items.append(item)
                    # Mark as seen
                    seen_listings[item_id] = datetime.now().isoformat()
            
            if new_items:
                print(f"Found {len(new_items)} NEW items in '{query_name}'!")
                total_new_items += len(new_items)
                
                # Send notification
                message = f"Found {len(new_items)} new items in {query_name}!"
                send_pushover_notification(message, f"New {query_name} Items!")
                
                # Show first few new items
                for i, item in enumerate(new_items[:3]):
                    title = item.get('title', 'No title')
                    price = item.get('currentPrice', 'No price')
                    print(f"  {i+1}. {title} - ${price}")
            else:
                print(f"No new items in '{query_name}'")
                
        except Exception as e:
            print(f"Error checking '{query_name}': {e}")
    
    # Save updated seen listings
    save_seen_listings(seen_listings)
    
    if total_new_items > 0:
        print(f"\n🎉 Total new items found: {total_new_items}")
    else:
        print("\nNo new items found in any searches")

if __name__ == "__main__":
    check_for_new_items()
