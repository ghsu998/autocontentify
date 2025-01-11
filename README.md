
# autocontentify

**AutoContentify GitHub Repository**: [autocontentify](https://github.com/ghsu998/autocontentify)

## AutoContentify File Structure
The project is organized as follows:

```
autocontentify/
├── config/
│   ├── __init__.py
│   ├── common.py
│   ├── credentials.pickle
│   ├── db_config.json
│   ├── google_ads_credentials.json
│   ├── google_ads.yaml
│   └── shopify_config.json
├── logs/
│   ├── common.log
│   ├── google_ads_api.log
│   ├── openai_api.log
│   └── sync_logs.log
├── modules/
│   ├── __init__.py
│   ├── api/
│   │   ├── generate_refresh_token.pygoogle_ads_api.py
│   │   ├── google_ads_api.py
│   │   ├── openai_api.py
│   │   ├── shopify_api.py
│   ├── database/
│   │   ├── db_connection.py
│   └── ecommerce/
│   │   ├── blog_generator_db_with_openai_module.py
│   │   ├── blog_sync_db_with_shopify_module.py
│   │   ├── google_ads_keyword_historical.py
│   │   ├── google_ads_keyword_plan.py
│   │   ├── google_ads_search_campaign_manager.py
│   │   ├── product_sync_db_with_shopify_module.py
├── venv/
│   ├── bin/
│   ├── include/
│   └── lib/
├── .env
├── .gitignore
├── app.py
├── main.py
├── README.md
└── requirements.txt
```

## AutoContentify Features
- **Google Ads Integration**: Automates keyword data retrieval and campaign creation.
- **Content Generation**: Generates SEO-optimized blogs using OpenAI API.
- **Shopify Sync**: Syncs generated content directly to Shopify stores.
- **Database Management**: Manages keywords and generated content with MySQL.

Dependencies are listed in `requirements.txt` for easy installation.
