#!/usr/bin/env python3

import json
import shopgoodwill

def test_multiple_searches():
    """Test multiple search terms to see what finds items"""
    print("Testing multiple ShopGoodwill searches...")
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Create ShopGoodwill instance
    auth_info = config['auth_info']
    sgw = shopgoodwill.Shopgoodwill(auth_info)
    
    # Test different search terms
    search_terms = [
        "gaylord",
        "electronics", 
        "laptop",
        "furniture",
        "chair"
    ]
    
    for term in search_terms:
        print(f"\nSearching for '{term}'...")
        try:
            results = sgw.get_query_results({
                "searchText": term,
                "lowPrice": "1",
                "highPrice": "1000"
            })
            
            print(f"Found {len(results)} results")
            if results and len(results) > 0:
                print(f"  First result: {results[0].get('title', 'No title')}")
                break  # Found something, stop here
                
        except Exception as e:
            print(f"Error searching for '{term}': {e}")

if __name__ == "__main__":
    test_multiple_searches()
