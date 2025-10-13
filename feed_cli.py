#!/usr/bin/env python3

import argparse
import json
import sys
from feed_system import FeedSystem

def main():
    parser = argparse.ArgumentParser(description='ShopGoodwill Feed System CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add search command
    add_parser = subparsers.add_parser('add', help='Add a new search')
    add_parser.add_argument('name', help='Search name')
    add_parser.add_argument('keywords', help='Keywords to search for (comma separated)')
    add_parser.add_argument('--min-price', type=float, help='Minimum price')
    add_parser.add_argument('--max-price', type=float, help='Maximum price')
    add_parser.add_argument('--category-ids', help='Category IDs (comma separated)')
    add_parser.add_argument('--pickup-only', action='store_true', help='Pickup only items')
    
    # List searches command
    subparsers.add_parser('list', help='List all searches')
    
    # Delete search command
    delete_parser = subparsers.add_parser('delete', help='Delete a search')
    delete_parser.add_argument('search_id', type=int, help='Search ID to delete')
    
    # Run search command
    run_parser = subparsers.add_parser('run', help='Run a search')
    run_parser.add_argument('search_id', type=int, help='Search ID to run')
    
    # Run all searches command
    subparsers.add_parser('run-all', help='Run all active searches')
    
    # Show results command
    results_parser = subparsers.add_parser('results', help='Show results')
    results_parser.add_argument('--search-id', type=int, help='Filter by search ID')
    results_parser.add_argument('--limit', type=int, default=20, help='Limit number of results')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    feed_system = FeedSystem()
    
    try:
        if args.command == 'add':
            search_id = feed_system.create_search(
                name=args.name,
                keywords=args.keywords,
                max_price=args.max_price,
                min_price=args.min_price,
                category_ids=args.category_ids,
                pickup_only=args.pickup_only
            )
            print(f"Search created with ID: {search_id}")
            
        elif args.command == 'list':
            searches = feed_system.get_searches()
            if not searches:
                print("No searches found")
                return
            
            print(f"{'ID':<5} {'Name':<20} {'Keywords':<30} {'Price Range':<15} {'Pickup':<8}")
            print("-" * 90)
            for search in searches:
                price_range = f"${search['min_price'] or 0}-${search['max_price'] or '∞'}"
                pickup = "Yes" if search['pickup_only'] else "No"
                print(f"{search['id']:<5} {search['name']:<20} {search['keywords']:<30} {price_range:<15} {pickup:<8}")
                
        elif args.command == 'delete':
            if feed_system.delete_search(args.search_id):
                print(f"Search {args.search_id} deleted successfully")
            else:
                print(f"Search {args.search_id} not found")
                
        elif args.command == 'run':
            results = feed_system.run_search(args.search_id)
            print(f"Found {len(results)} new items")
            for result in results:
                print(f"  - {result['title']} (${result['current_price']}) - {result['url']}")
                
        elif args.command == 'run-all':
            searches = feed_system.get_searches()
            total_new = 0
            for search in searches:
                try:
                    results = feed_system.run_search(search['id'])
                    print(f"Search '{search['name']}': {len(results)} new items")
                    total_new += len(results)
                except Exception as e:
                    print(f"Error running search '{search['name']}': {e}")
            print(f"Total new items found: {total_new}")
            
        elif args.command == 'results':
            results = feed_system.get_results(args.search_id, args.limit)
            if not results:
                print("No results found")
                return
            
            print(f"{'Title':<50} {'Price':<10} {'Search':<15} {'URL'}")
            print("-" * 100)
            for result in results:
                title = result['title'][:47] + "..." if len(result['title']) > 50 else result['title']
                print(f"{title:<50} ${result['current_price']:<9} {result['search_name']:<15} {result['url']}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
