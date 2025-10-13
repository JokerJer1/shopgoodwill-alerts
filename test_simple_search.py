#!/usr/bin/env python3

import json
import shopgoodwill

def test_simple_search():
    """Test a simple search to see what works"""
    print("Testing simple ShopGoodwill search...")
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Create ShopGoodwill instance
    auth_info = config['auth_info']
    sgw = shopgoodwill.Shopgoodwill(auth_info)
    
    # Try a very simple search first
    print("Testing basic search...")
    try:
        # Use minimal search parameters
        results = sgw.get_query_results({
            "searchText": "gaylord"
        })
        print(f"✅ Basic search worked! Found {len(results)} results")
        if results:
            print(f"First result: {results[0].get('title', 'No title')}")
    except Exception as e:
        print(f"❌ Basic search failed: {e}")
    
    # Try with more parameters
    print("\nTesting with price range...")
    try:
        results = sgw.get_query_results({
            "searchText": "gaylord",
            "lowPrice": "1",
            "highPrice": "1000"
        })
        print(f"✅ Price range search worked! Found {len(results)} results")
    except Exception as e:
        print(f"❌ Price range search failed: {e}")
    
    # Try a different search term
    print("\nTesting with 'electronics'...")
    try:
        results = sgw.get_query_results({
            "searchText": "electronics"
        })
        print(f"✅ Electronics search worked! Found {len(results)} results")
    except Exception as e:
        print(f"❌ Electronics search failed: {e}")

if __name__ == "__main__":
    test_simple_search()
