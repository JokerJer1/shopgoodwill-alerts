#!/usr/bin/env python3

import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from flask import Flask, jsonify, request, render_template_string
import shopgoodwill

app = Flask(__name__)

# Database setup
def init_db():
    conn = sqlite3.connect('feed_system.db')
    cursor = conn.cursor()
    
    # Create searches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            keywords TEXT NOT NULL,
            max_price REAL,
            min_price REAL,
            category_ids TEXT,
            pickup_only BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT TRUE
        )
    ''')
    
    # Create results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            search_id INTEGER,
            item_id TEXT UNIQUE NOT NULL,
            title TEXT,
            current_price REAL,
            end_time TEXT,
            url TEXT,
            image_url TEXT,
            seller_name TEXT,
            found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (search_id) REFERENCES searches (id)
        )
    ''')
    
    conn.commit()
    conn.close()

class FeedSystem:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.sgw = None
        self.load_config()
        
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            
            # Initialize ShopGoodwill connection if auth info is available
            auth_info = self.config.get('auth_info')
            if auth_info and (auth_info.get('username') or auth_info.get('access_token')):
                self.sgw = shopgoodwill.Shopgoodwill(auth_info)
        else:
            self.config = {}
    
    def create_search(self, name: str, keywords: str, max_price: Optional[float] = None, 
                     min_price: Optional[float] = None, category_ids: Optional[str] = None,
                     pickup_only: bool = False) -> int:
        """Create a new keyword search"""
        conn = sqlite3.connect('feed_system.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO searches (name, keywords, max_price, min_price, category_ids, pickup_only)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, keywords, max_price, min_price, category_ids, pickup_only))
            
            search_id = cursor.lastrowid
            conn.commit()
            return search_id
        except sqlite3.IntegrityError:
            raise ValueError(f"Search with name '{name}' already exists")
        finally:
            conn.close()
    
    def get_searches(self) -> List[Dict]:
        """Get all active searches"""
        conn = sqlite3.connect('feed_system.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, keywords, max_price, min_price, category_ids, pickup_only, created_at
            FROM searches WHERE active = TRUE
            ORDER BY created_at DESC
        ''')
        
        searches = []
        for row in cursor.fetchall():
            searches.append({
                'id': row[0],
                'name': row[1],
                'keywords': row[2],
                'max_price': row[3],
                'min_price': row[4],
                'category_ids': row[5],
                'pickup_only': bool(row[6]),
                'created_at': row[7]
            })
        
        conn.close()
        return searches
    
    def delete_search(self, search_id: int) -> bool:
        """Delete a search"""
        conn = sqlite3.connect('feed_system.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE searches SET active = FALSE WHERE id = ?', (search_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def build_query_from_search(self, search: Dict) -> Dict:
        """Build a ShopGoodwill query from a search configuration"""
        query = {
            "isSize": False,
            "isWeddingCatagory": "false",
            "isMultipleCategoryIds": False,
            "isFromHeaderMenuTab": False,
            "layout": "",
            "searchText": search['keywords'],
            "selectedGroup": "",
            "selectedCategoryIds": search.get('category_ids', ''),
            "selectedSellerIds": "",
            "lowPrice": str(search.get('min_price', 0)),
            "highPrice": str(search.get('max_price', 999999)),
            "searchBuyNowOnly": "",
            "searchPickupOnly": "true" if search.get('pickup_only', False) else "false",
            "searchNoPickupOnly": "false",
            "searchOneCentShippingOnly": "false",
            "searchDescriptions": "true",  # Search in descriptions for keywords
            "searchClosedAuctions": "false",
            "closedAuctionEndingDate": "1/1/1",
            "closedAuctionDaysBack": "7",
            "searchCanadaShipping": "false",
            "searchInternationalShippingOnly": "false",
            "sortColumn": "1",
            "sortDescending": "false",
            "savedSearchId": 0,
            "useBuyerPrefs": "true",
            "searchUSOnlyShipping": "false",
            "categoryLevelNo": "1",
            "categoryLevel": 1,
            "categoryId": 0,
            "partNumber": "",
            "catIds": search.get('category_ids', '')
        }
        return query
    
    def run_search(self, search_id: int) -> List[Dict]:
        """Run a specific search and return new results"""
        if not self.sgw:
            raise Exception("ShopGoodwill authentication required")
        
        conn = sqlite3.connect('feed_system.db')
        cursor = conn.cursor()
        
        # Get search details
        cursor.execute('SELECT * FROM searches WHERE id = ? AND active = TRUE', (search_id,))
        search_row = cursor.fetchone()
        
        if not search_row:
            conn.close()
            raise ValueError("Search not found or inactive")
        
        search = {
            'id': search_row[0],
            'name': search_row[1],
            'keywords': search_row[2],
            'max_price': search_row[3],
            'min_price': search_row[4],
            'category_ids': search_row[5],
            'pickup_only': bool(search_row[6])
        }
        
        # Build and run query
        query = self.build_query_from_search(search)
        results = self.sgw.get_query_results(query)
        
        new_results = []
        for item in results:
            item_id = str(item['itemId'])
            
            # Check if we've already seen this item
            cursor.execute('SELECT id FROM results WHERE item_id = ?', (item_id,))
            if cursor.fetchone():
                continue
            
            # Store new result
            cursor.execute('''
                INSERT INTO results (search_id, item_id, title, current_price, end_time, url, image_url, seller_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                search_id,
                item_id,
                item.get('title', ''),
                item.get('minimumBid', 0),
                item.get('endTime', ''),
                f"https://shopgoodwill.com/item/{item_id}",
                item.get('imageUrl', ''),
                item.get('sellerName', '')
            ))
            
            new_results.append({
                'item_id': item_id,
                'title': item.get('title', ''),
                'current_price': item.get('minimumBid', 0),
                'end_time': item.get('endTime', ''),
                'url': f"https://shopgoodwill.com/item/{item_id}",
                'image_url': item.get('imageUrl', ''),
                'seller_name': item.get('sellerName', ''),
                'remaining_time': item.get('remainingTime', '')
            })
        
        conn.commit()
        conn.close()
        
        return new_results
    
    def get_results(self, search_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """Get results for a search or all searches"""
        conn = sqlite3.connect('feed_system.db')
        cursor = conn.cursor()
        
        if search_id:
            cursor.execute('''
                SELECT r.*, s.name as search_name
                FROM results r
                JOIN searches s ON r.search_id = s.id
                WHERE r.search_id = ?
                ORDER BY r.found_at DESC
                LIMIT ?
            ''', (search_id, limit))
        else:
            cursor.execute('''
                SELECT r.*, s.name as search_name
                FROM results r
                JOIN searches s ON r.search_id = s.id
                ORDER BY r.found_at DESC
                LIMIT ?
            ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'search_id': row[1],
                'item_id': row[2],
                'title': row[3],
                'current_price': row[4],
                'end_time': row[5],
                'url': row[6],
                'image_url': row[7],
                'seller_name': row[8],
                'found_at': row[9],
                'search_name': row[10]
            })
        
        conn.close()
        return results

# Initialize the feed system
feed_system = FeedSystem()
init_db()

# Web interface HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>ShopGoodwill Feed System</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .search-form { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 5px; }
        .search-form input, .search-form select { margin: 5px; padding: 8px; }
        .search-form button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .search-form button:hover { background: #0056b3; }
        .searches { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }
        .search-card { border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        .search-card h3 { margin-top: 0; }
        .results { margin-top: 20px; }
        .result-item { border: 1px solid #eee; padding: 10px; margin: 10px 0; border-radius: 3px; }
        .result-item h4 { margin: 0 0 10px 0; }
        .result-item a { color: #007bff; text-decoration: none; }
        .result-item a:hover { text-decoration: underline; }
        .price { font-weight: bold; color: #28a745; }
        .delete-btn { background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }
        .delete-btn:hover { background: #c82333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>ShopGoodwill Feed System</h1>
        
        <div class="search-form">
            <h3>Add New Search</h3>
            <form id="searchForm">
                <input type="text" name="name" placeholder="Search Name" required>
                <input type="text" name="keywords" placeholder="Keywords (comma separated)" required>
                <input type="number" name="min_price" placeholder="Min Price" step="0.01">
                <input type="number" name="max_price" placeholder="Max Price" step="0.01">
                <input type="text" name="category_ids" placeholder="Category IDs (comma separated)">
                <label>
                    <input type="checkbox" name="pickup_only"> Pickup Only
                </label>
                <button type="submit">Add Search</button>
            </form>
        </div>
        
        <div class="searches" id="searches">
            <!-- Searches will be loaded here -->
        </div>
        
        <div class="results" id="results">
            <!-- Results will be loaded here -->
        </div>
    </div>

    <script>
        // Load searches on page load
        loadSearches();
        loadResults();
        
        // Handle search form submission
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            // Convert checkbox to boolean
            data.pickup_only = formData.has('pickup_only');
            
            try {
                const response = await fetch('/api/searches', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    e.target.reset();
                    loadSearches();
                } else {
                    alert('Error creating search');
                }
            } catch (error) {
                alert('Error creating search: ' + error.message);
            }
        });
        
        async function loadSearches() {
            try {
                const response = await fetch('/api/searches');
                const searches = await response.json();
                
                const container = document.getElementById('searches');
                container.innerHTML = searches.map(search => `
                    <div class="search-card">
                        <h3>${search.name}</h3>
                        <p><strong>Keywords:</strong> ${search.keywords}</p>
                        <p><strong>Price Range:</strong> $${search.min_price || 0} - $${search.max_price || '∞'}</p>
                        <p><strong>Pickup Only:</strong> ${search.pickup_only ? 'Yes' : 'No'}</p>
                        <p><strong>Created:</strong> ${new Date(search.created_at).toLocaleDateString()}</p>
                        <button class="delete-btn" onclick="deleteSearch(${search.id})">Delete</button>
                        <button onclick="runSearch(${search.id})">Run Search</button>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading searches:', error);
            }
        }
        
        async function loadResults() {
            try {
                const response = await fetch('/api/results');
                const results = await response.json();
                
                const container = document.getElementById('results');
                container.innerHTML = `
                    <h3>Recent Results</h3>
                    ${results.map(result => `
                        <div class="result-item">
                            <h4><a href="${result.url}" target="_blank">${result.title}</a></h4>
                            <p class="price">$${result.current_price}</p>
                            <p><strong>Search:</strong> ${result.search_name}</p>
                            <p><strong>Seller:</strong> ${result.seller_name}</p>
                            <p><strong>Ends:</strong> ${new Date(result.end_time).toLocaleString()}</p>
                        </div>
                    `).join('')}
                `;
            } catch (error) {
                console.error('Error loading results:', error);
            }
        }
        
        async function deleteSearch(searchId) {
            if (confirm('Are you sure you want to delete this search?')) {
                try {
                    const response = await fetch(`/api/searches/${searchId}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        loadSearches();
                    } else {
                        alert('Error deleting search');
                    }
                } catch (error) {
                    alert('Error deleting search: ' + error.message);
                }
            }
        }
        
        async function runSearch(searchId) {
            try {
                const response = await fetch(`/api/searches/${searchId}/run`, {
                    method: 'POST'
                });
                
                const result = await response.json();
                alert(`Found ${result.new_results} new items`);
                loadResults();
            } catch (error) {
                alert('Error running search: ' + error.message);
            }
        }
    </script>
</body>
</html>
'''

# API Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/searches', methods=['GET'])
def get_searches():
    return jsonify(feed_system.get_searches())

@app.route('/api/searches', methods=['POST'])
def create_search():
    data = request.get_json()
    
    try:
        search_id = feed_system.create_search(
            name=data['name'],
            keywords=data['keywords'],
            max_price=float(data.get('max_price')) if data.get('max_price') else None,
            min_price=float(data.get('min_price')) if data.get('min_price') else None,
            category_ids=data.get('category_ids'),
            pickup_only=data.get('pickup_only', False)
        )
        return jsonify({'id': search_id, 'message': 'Search created successfully'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/searches/<int:search_id>', methods=['DELETE'])
def delete_search(search_id):
    if feed_system.delete_search(search_id):
        return jsonify({'message': 'Search deleted successfully'})
    else:
        return jsonify({'error': 'Search not found'}), 404

@app.route('/api/searches/<int:search_id>/run', methods=['POST'])
def run_search(search_id):
    try:
        results = feed_system.run_search(search_id)
        return jsonify({'new_results': len(results), 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/results')
def get_results():
    search_id = request.args.get('search_id', type=int)
    limit = request.args.get('limit', 50, type=int)
    
    results = feed_system.get_results(search_id, limit)
    return jsonify(results)

@app.route('/api/feed/<int:search_id>.json')
def get_feed_json(search_id):
    """Get JSON feed for a specific search"""
    results = feed_system.get_results(search_id, 100)
    return jsonify({
        'search_id': search_id,
        'results': results,
        'generated_at': datetime.now().isoformat()
    })

@app.route('/api/feed/<int:search_id>.rss')
def get_feed_rss(search_id):
    """Get RSS feed for a specific search"""
    results = feed_system.get_results(search_id, 50)
    
    rss = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>ShopGoodwill Feed - Search {search_id}</title>
        <description>ShopGoodwill search results feed</description>
        <link>http://localhost:5000</link>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
'''
    
    for result in results:
        rss += f'''
        <item>
            <title>{result['title']}</title>
            <description>Price: ${result['current_price']} | Seller: {result['seller_name']}</description>
            <link>{result['url']}</link>
            <guid>{result['item_id']}</guid>
            <pubDate>{datetime.fromisoformat(result['found_at'].replace('Z', '+00:00')).strftime('%a, %d %b %Y %H:%M:%S GMT')}</pubDate>
        </item>
'''
    
    rss += '''
    </channel>
</rss>'''
    
    return rss, 200, {'Content-Type': 'application/rss+xml'}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
