import requests
import logging
import json
import os
from datetime import datetime
from modules.database.db_connection import connect_db

# Set up logging configuration for better readability
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration file
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../config/shopify_config.json"))

def load_config():
    """Load the Shopify configuration file"""
    logging.info("Loading Shopify configuration...")
    try:
        with open(CONFIG_PATH, "r") as config_file:
            config = json.load(config_file)
            logging.info("Shopify configuration loaded successfully.")
            return config
    except FileNotFoundError:
        logging.error("Configuration file not found. Please ensure the file exists.")
        raise
    except json.JSONDecodeError:
        logging.error("Error decoding the Shopify configuration JSON.")
        raise
    except Exception as e:
        logging.error(f"Error loading Shopify configuration: {e}")
        raise

# Load the configuration
config = load_config()
SHOPIFY_STORE_URL = config["SHOPIFY_STORE_URL"]
ACCESS_TOKEN = config["ACCESS_TOKEN"]
BLOG_ID = config["BLOG_ID"]

# HTTP headers for Shopify API requests
headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

def make_request(url):
    """General function to make GET requests with retry logic"""
    logging.info(f"Making request to URL: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logging.info(f"Request to {url} successful.")
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during API request: {e}")
    return None

def get_shopify_blogs():
    """Fetch Shopify blog articles"""
    logging.info("Fetching Shopify blog articles...")
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/blogs/{BLOG_ID}/articles.json"
    data = make_request(url)
    
    if data:
        articles = data.get("articles", [])
        logging.info(f"Fetched {len(articles)} articles from Shopify.")
        return articles
    logging.error("Failed to fetch Shopify blogs.")
    return []

def get_shopify_products():
    """Fetch Shopify products data"""
    logging.info("Fetching Shopify products data...")
    url = f"{SHOPIFY_STORE_URL}/admin/api/2023-10/products.json?limit=250"
    products = []

    while url:
        data = make_request(url)
        if data:
            products_page = data.get("products", [])
            products.extend(products_page)
            logging.info(f"Fetched {len(products_page)} products from Shopify. Total so far: {len(products)}")
            # Get next page if available
            url = data.get("next", {}).get("url", None)
        else:
            break

    logging.info(f"Total products fetched: {len(products)}")
    return products

if __name__ == "__main__":
    logging.info("Starting the Shopify integration script...")
    get_shopify_blogs()
    get_shopify_products()
    logging.info("Script execution completed.")