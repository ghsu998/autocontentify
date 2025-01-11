import os
import sys
import json
import datetime
from openai import OpenAI
from config.common import BASE_DIR, CONFIG_DIR, setup_logger
from modules.api.openai_api import generate_rsa_text
from modules.database.db_connection import fetch_keywords_from_database
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# 日記初始化
logger = setup_logger(script_name="google_ads_api")

# 全局配置文件路徑
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "google_ads_credentials.json")
CONFIG_PATH = os.path.join(CONFIG_DIR, "google_ads.yaml")

# 工具函數：校驗文件是否存在
def check_file_exists(file_path, description):
    logger.debug(f"Checking if file exists: {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"❌ {description} 不存在: {file_path}")
        sys.exit(1)

# 校驗所需的配置文件是否存在
check_file_exists(CREDENTIALS_PATH, "Google Ads 憑據文件")
check_file_exists(CONFIG_PATH, "Google Ads 配置文件")

# 工具函數：校驗 JSON 文件內容
def validate_json_file(file_path, required_keys):
    logger.debug(f"Validating JSON file: {file_path}")
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        
        # 確保 "installed" 鍵存在於 JSON 文件中
        if "installed" not in data:
            raise ValueError("❌ 配置文件中缺少 'installed' 鍵")

        nested_data = data["installed"]
        missing_keys = [key for key in required_keys if key not in nested_data]
        if missing_keys:
            logger.warning(f"Missing keys: {missing_keys}")
            raise ValueError(f"缺少必要字段: {missing_keys}")
        
        return nested_data  # 返回嵌套的內容
    except Exception as e:
        logger.error(f"❌ 配置文件校驗失敗: {file_path} -> {e}")
        sys.exit(1)

# 加載 Google Ads 客戶端
def load_google_ads_client():
    logger.debug("Loading Google Ads client")
    try:
        credentials = validate_json_file(CREDENTIALS_PATH, ["login_customer_id"])
        google_ads_client = GoogleAdsClient.load_from_storage(CONFIG_PATH)
        google_ads_client.login_customer_id = credentials["login_customer_id"]
        logger.info(f"✅ 成功加載 Google Ads 客戶端, Login Customer ID: {google_ads_client.login_customer_id}")
        return google_ads_client
    except Exception as e:
        logger.error(f"❌ 加載 Google Ads 客戶端失敗: {e}")
        raise

def generate_name(prefix, entity_type):
    logger.debug(f"Generating name with prefix: {prefix}, entity_type: {entity_type}")
    now = datetime.datetime.now()
    return f"{prefix} {entity_type} - {now.strftime('%Y-%m-%d-%H%M%S')}"

def create_campaign(client, customer_id, campaign_type="SEARCH", budget=10000000, locations=None, languages=None):
    logger.debug("Creating campaign")
    try:
        if budget is None:
            budget = 10000000
        if locations is None:
            locations = ["2840"]  # 美國
        if languages is None:
            languages = ["1000"]  # 英語
        campaign_service = client.get_service("CampaignService")
        campaign_budget_service = client.get_service("CampaignBudgetService")
        campaign_budget_operation = client.get_type("CampaignBudgetOperation")
        campaign_budget = campaign_budget_operation.create
        campaign_budget.name = generate_name(campaign_type, "Budget")
        campaign_budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD
        campaign_budget.amount_micros = budget
        logger.debug("Creating campaign budget")
        budget_response = campaign_budget_service.mutate_campaign_budgets(
            customer_id=customer_id, operations=[campaign_budget_operation]
        )
        budget_resource_name = budget_response.results[0].resource_name
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        campaign.name = generate_name(campaign_type, "Campaign")
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        campaign.campaign_budget = budget_resource_name
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.manual_cpc.enhanced_cpc_enabled = False
        logger.debug("Creating campaign")
        campaign_response = campaign_service.mutate_campaigns(
            customer_id=customer_id, operations=[campaign_operation]
        )
        campaign_resource_name = campaign_response.results[0].resource_name
        logger.info(f"✅ 廣告系列已創建: {campaign.name}")
        return campaign_resource_name
    except Exception as e:
        logger.error(f"❌ 無法創建廣告系列: {e}")
        raise

def create_ad_group(client, customer_id, campaign_id):
    logger.debug("Creating ad group")
    try:
        ad_group_service = client.get_service("AdGroupService")
        ad_group_operation = client.get_type("AdGroupOperation")
        ad_group = ad_group_operation.create
        ad_group.name = generate_name("", "Ad Group")
        ad_group.campaign = campaign_id
        ad_group.status = client.enums.AdGroupStatusEnum.ENABLED
        ad_group.cpc_bid_micros = 1000000

        logger.debug("Sending request to create ad group")
        ad_group_response = ad_group_service.mutate_ad_groups(
            customer_id=customer_id, operations=[ad_group_operation]
        )
        ad_group_resource_name = ad_group_response.results[0].resource_name
        logger.info(f"✅ 廣告組已創建: {ad_group.name}")
        return ad_group_resource_name
    except GoogleAdsException as ex:
        logger.error(f"❌ Google Ads API 錯誤：{ex.failure}")
        raise
    except Exception as e:
        logger.error(f"❌ 創建廣告組失敗：{e}")
        raise

def create_google_ads_rsa_workflow(client, openai_client, customer_id, ad_group_id):
    logger.debug("Starting RSA workflow")
    try:
        logger.info("Fetching keywords from the database...")
        keywords = fetch_keywords_from_database()
        if not keywords:
            raise ValueError("No keywords found in the database.")

        logger.info(f"Fetched keywords: {keywords}")

        logger.info("Generating RSA text using OpenAI...")
        rsa_text = generate_rsa_text(client=openai_client, keywords=keywords[:15])
        if not rsa_text.get("headlines") or not rsa_text.get("descriptions"):
            raise ValueError("OpenAI failed to generate RSA text.")

        logger.info(f"Generated RSA text: {rsa_text}")

        logger.info("Creating RSA ad...")
        ad_resource_name = _create_rsa_ad(client, customer_id, ad_group_id, rsa_text)
        logger.info(f"RSA ad created successfully: {ad_resource_name}")
        return ad_resource_name

    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise

def _create_rsa_ad(client, customer_id: str, ad_group_id: str, rsa_text: dict):
    logger.debug("Creating RSA ad")
    try:
        if not rsa_text.get("headlines") or not rsa_text.get("descriptions"):
            logger.error(f"Incomplete RSA text data: {rsa_text}")
            raise ValueError("Incomplete RSA text data.")

        ad_group_ad_service = client.get_service("AdGroupAdService")
        ad_group_ad_operation = client.get_type("AdGroupAdOperation")
        ad_group_ad = ad_group_ad_operation.create
        ad_group_ad.ad_group = ad_group_id
        ad_group_ad.status = client.enums.AdGroupAdStatusEnum.ENABLED

        # Add headlines and descriptions
        rsa_info = ad_group_ad.ad.responsive_search_ad
        for headline in rsa_text["headlines"]:
            headline_part = client.get_type("AdTextAsset")
            headline_part.text = headline
            rsa_info.headlines.append(headline_part)

        for description in rsa_text["descriptions"]:
            description_part = client.get_type("AdTextAsset")
            description_part.text = description
            rsa_info.descriptions.append(description_part)

        # Add final URL
        final_url = "https://www.greenewrap.com"
        ad_group_ad.ad.final_urls.append(final_url)
        logger.info(f"Final URL set: {final_url}")

        # Send request
        logger.debug("Sending request to create RSA ad")
        response = ad_group_ad_service.mutate_ad_group_ads(
            customer_id=customer_id, operations=[ad_group_ad_operation]
        )
        ad_resource_name = response.results[0].resource_name
        logger.info(f"Ad created successfully: {ad_resource_name}")
        return ad_resource_name

    except GoogleAdsException as e:
        logger.error(f"Google Ads API Error: {e.failure}")
        raise
    except Exception as e:
        logger.error(f"Failed to create RSA ad: {e}")
        raise

if __name__ == "__main__":
    logger.info("啟動程序，開始測試 Google Ads API 日記功能")
    print("啟動程序，開始測試 Google Ads API 日記功能")
    try:
        # 加載 Google Ads 客戶端
        client = load_google_ads_client()

        # 初始化 OpenAI 客戶端（假設已正確配置）
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Google Ads 客戶 ID
        customer_id = "5141511711"

        # Step 1: 創建廣告系列
        try:
            logger.info("開始創建廣告系列...")
            print("開始創建廣告系列...")
            campaign_id = create_campaign(client, customer_id, campaign_type="SEARCH")
            logger.info(f"✅ 廣告系列已創建，ID: {campaign_id}")
            print(f"✅ 廣告系列已創建，ID: {campaign_id}")
        except Exception as e:
            logger.error(f"❌ 創建廣告系列失敗：{e}")
            print(f"❌ 創建廣告系列失敗：{e}")
            raise

        # Step 2: 創建廣告組
        try:
            logger.info("開始創建廣告組...")
            print("開始創建廣告組...")
            ad_group_id = create_ad_group(client, customer_id, campaign_id)
            logger.info(f"✅ 廣告組已創建，ID: {ad_group_id}")
            print(f"✅ 廣告組已創建，ID: {ad_group_id}")
        except Exception as e:
            logger.error(f"❌ 創建廣告組失敗：{e}")
            print(f"❌ 創建廣告組失敗：{e}")
            raise

        # Step 3: 生成 RSA 文案並創建廣告
        try:
            logger.info("開始整合 RSA 廣告創建流程...")
            print("開始整合 RSA 廣告創建流程...")

            # 使用整合的工作流函數創建廣告
            rsa_ad_id = create_google_ads_rsa_workflow(client, openai_client, customer_id, ad_group_id)

            logger.info(f"✅ 創建的 RSA 廣告 ID: {rsa_ad_id}")
            print(f"✅ 創建的 RSA 廣告 ID: {rsa_ad_id}")
        except Exception as e:
            logger.error(f"❌ 創建 RSA 廣告失敗：{e}")
            print(f"❌ 創建 RSA 廣告失敗：{e}")

        logger.info("所有步驟執行完畢！")
        print("✅ 所有步驟執行完畢！")

    except Exception as e:
        logger.error(f"❌ 程序執行失敗：{e}")
        print(f"❌ 程序執行失敗：{e}")
