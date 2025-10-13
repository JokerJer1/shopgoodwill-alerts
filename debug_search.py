#!/usr/bin/env python3

import json
import subprocess

def debug_search():
    """Debug the search to see what's happening"""
    print("Running ShopGoodwill search in debug mode...")
    
    # Run the alert script with verbose output
    result = subprocess.run(['python', 'alert_on_new_query_results.py', '--all'], 
                          capture_output=True, text=True)
    
    print("=== STDOUT ===")
    print(result.stdout)
    print("\n=== STDERR ===")
    print(result.stderr)
    print(f"\n=== RETURN CODE: {result.returncode} ===")

if __name__ == "__main__":
    debug_search()
