import subprocess
import logging
import os

# 確保日誌目錄存在
log_directory = "AutoContentify/logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 配置全局日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=os.path.join(log_directory, "sync_logs.log")
)

logging.info("✅ 全局日誌已配置，輸出到 sync_logs.log")


def run_google_ads_keyword_plan():
    """Run the Google Ads Keyword Plan script."""
    print("Running Google Ads Keyword Plan...")
    script_path = os.path.join(os.path.dirname(__file__), "google_ads_keyword_plan.py")
    subprocess.run(["python", script_path])

def run_google_ads_keyword_historical():
    """Run the Google Ads Keyword Historical script."""
    print("Running Google Ads Keyword Historical...")
    script_path = os.path.join(os.path.dirname(__file__), "google_ads_keyword_historical.py")
    subprocess.run(["python", script_path])

def run_blog_generator():
    """Run the Blog Generator script."""
    print("Running Blog Generator with OpenAI...")
    script_path = os.path.join(os.path.dirname(__file__), "blog_generator_db_with_openai_module.py")
    subprocess.run(["python", script_path])

def run_blog_sync_with_shopify():
    """Run the Blog Sync script to Shopify."""
    print("Running Blog Sync with Shopify...")
    script_path = os.path.join(os.path.dirname(__file__), "blog_sync_db_with_shopify_module.py")
    subprocess.run(["python", script_path])

def run_product_sync_with_shopify():
    """Run the Product Sync script to sync products from Shopify to the local database."""
    print("Running Product Sync with Shopify...")
    script_path = os.path.join(os.path.dirname(__file__), "product_sync_db_with_shopify_module.py")
    subprocess.run(["python", script_path])

def main():
    # Example flow, you can customize the order or conditions
    run_google_ads_keyword_plan()
    run_google_ads_keyword_historical()
    run_blog_generator()
    run_blog_sync_with_shopify()
    run_product_sync_with_shopify()  # Added product sync step


if __name__ == "__main__":
    main()




