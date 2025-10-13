# ShopGoodwill Feed System

A web-based feed system for ShopGoodwill keyword searches built on top of the existing ShopGoodwill scripts.

## Features

- **Keyword-based searches**: Set up searches with specific keywords
- **Price filtering**: Set minimum and maximum price ranges
- **Category filtering**: Filter by specific category IDs
- **Pickup-only filtering**: Find items available for local pickup
- **Web interface**: Easy-to-use web interface for managing searches
- **API endpoints**: JSON and RSS feeds for integration
- **CLI tool**: Command-line interface for automation
- **Real-time results**: Get notified of new items matching your criteria

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure authentication in `feed_config.json`:
```json
{
    "auth_info": {
        "username": "your_username",
        "password": "your_password"
    }
}
```

## Usage

### Web Interface

Start the web server:
```bash
python feed_system.py
```

Then open your browser to `http://localhost:5000`

### CLI Interface

Add a new search:
```bash
python feed_cli.py add "Electronics" "laptop,computer" --min-price 10 --max-price 500
```

List all searches:
```bash
python feed_cli.py list
```

Run a specific search:
```bash
python feed_cli.py run 1
```

Run all searches:
```bash
python feed_cli.py run-all
```

Show recent results:
```bash
python feed_cli.py results --limit 20
```

### API Endpoints

- `GET /api/searches` - List all searches
- `POST /api/searches` - Create a new search
- `DELETE /api/searches/{id}` - Delete a search
- `POST /api/searches/{id}/run` - Run a specific search
- `GET /api/results` - Get recent results
- `GET /api/feed/{id}.json` - JSON feed for a search
- `GET /api/feed/{id}.rss` - RSS feed for a search

## Search Configuration

When creating a search, you can specify:

- **Name**: A descriptive name for your search
- **Keywords**: Comma-separated keywords to search for
- **Min/Max Price**: Price range filtering
- **Category IDs**: Specific category IDs to search in
- **Pickup Only**: Only show items available for local pickup

## Examples

### Electronics Search
```bash
python feed_cli.py add "Electronics" "laptop,computer,tablet" --min-price 50 --max-price 1000
```

### Local Pickup Only
```bash
python feed_cli.py add "Local Items" "furniture,appliances" --pickup-only
```

### Specific Category
```bash
python feed_cli.py add "Jewelry" "ring,necklace,watch" --category-ids "123,456"
```

## Automation

You can set up cron jobs to automatically run searches:

```bash
# Run all searches every 5 minutes
*/5 * * * * cd /path/to/feed && python feed_cli.py run-all
```

## Integration

The system provides JSON and RSS feeds that can be integrated with other services:

- **JSON Feed**: `http://localhost:5000/api/feed/1.json`
- **RSS Feed**: `http://localhost:5000/api/feed/1.rss`

## Database

The system uses SQLite to store searches and results. The database file is created automatically as `feed_system.db`.

## Troubleshooting

1. **Authentication errors**: Make sure your ShopGoodwill credentials are correct in `feed_config.json`
2. **No results**: Check that your keywords are spelled correctly and try broader terms
3. **Database errors**: Delete `feed_system.db` to reset the database

## Advanced Usage

### Custom Query Parameters

You can modify the `build_query_from_search` method in `feed_system.py` to add more advanced filtering options.

### Webhook Integration

Add webhook support by modifying the `run_search` method to send HTTP requests to external services when new items are found.

### Email Notifications

Integrate with the existing ShopGoodwill scripts' notification system by adding email/SMS alerts for new results.
