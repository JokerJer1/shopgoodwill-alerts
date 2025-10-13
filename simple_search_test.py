#!/usr/bin/env python3

import json
import shopgoodwill

def test_search():
    """Test a simple search to see if we can find any items"""
    print("Testing ShopGoodwill search...")
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Create ShopGoodwill instance
    auth_info = config['auth_info']
    sgw = shopgoodwill.Shopgoodwill(auth_info)
    
    # Test a simple search
    print("Searching for 'gaylord'...")
    try:
        results = sgw.get_query_results({
            "searchText": "gaylord",
            "lowPrice": "5",
            "highPrice": "50000"
        })
        
        print(f"Found {len(results)} results")
        if results:
            print("First few results:")
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. {result.get('title', 'No title')} - ${result.get('currentPrice', 'No price')}")
        else:
            print("No results found for 'gaylord' search")
            
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    test_search()
