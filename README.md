# ShopGoodwill Alerts

Automated monitoring for ShopGoodwill items with Pushover notifications.

## Features

- 🔍 **Automated searches** for specific items
- 📱 **Push notifications** via Pushover
- 🔗 **Direct links** to found items
- 💰 **Price information** included
- ⏰ **24/7 monitoring** via GitHub Actions

## Setup

1. Fork this repository
2. Add your secrets in GitHub repository settings:
   - `SHOPGOODWILL_USERNAME` - Your ShopGoodwill username
   - `SHOPGOODWILL_PASSWORD` - Your ShopGoodwill password
   - `PUSHOVER_TOKEN` - Your Pushover app token
   - `PUSHOVER_USER` - Your Pushover user key

3. The workflow will run automatically every 10 minutes

## Configuration

Edit `config-github.json` to modify:
- Search terms
- Price ranges
- Notification settings

## Manual Run

You can trigger a manual run in the GitHub Actions tab.