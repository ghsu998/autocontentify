from modules.api.google_ads_api import (
    load_google_ads_client,
    create_campaign,
    create_ad_group,
    create_rsa_ad_text,
    create_rsa_ad,
)
from modules.database.db_connection import connect_db


def fetch_company_website():
    """Fetch the website URL for the company from the database."""
    connection = connect_db()
    cursor = connection.cursor()
    query = "SELECT website FROM ecommerce_data_db.companies WHERE id = 1"
    cursor.execute(query)
    website = cursor.fetchone()
    connection.close()
    return website[0] if website else None


def fetch_keywords():
    """Fetch keywords from the database with minimum average monthly searches."""
    connection = connect_db()
    cursor = connection.cursor()
    query = "SELECT keyword FROM ecommerce_data_db.keywords WHERE avg_monthly_searches >= 100"
    cursor.execute(query)
    keywords = cursor.fetchall()
    connection.close()

    # Return the list of keywords
    return [keyword[0] for keyword in keywords]


def main():
    # Load the Google Ads client
    googleads_client = load_google_ads_client()
    if not googleads_client:
        print("❌ Failed to load Google Ads client.")
        return

    customer_id = googleads_client.login_customer_id
    print(f"✅ Using Customer ID: {customer_id}")

    # Fetch the required data
    keywords = fetch_keywords()
    website_url = fetch_company_website()

    # Create a campaign
    campaign_id = create_campaign(
        googleads_client,
        customer_id,
        campaign_name="Search Campaign Example",
    )

    # Ensure campaign creation was successful
    if not campaign_id:
        print("❌ Campaign creation failed or campaign already exists.")
        return

    # Create an ad group
    ad_group_id = create_ad_group(
        googleads_client,
        customer_id,
        campaign_id,
        ad_group_name="Search Ad Group Example",
    )

    # Ensure ad group creation was successful
    if not ad_group_id:
        print("❌ Ad Group creation failed or ad group already exists.")
        return

    # Generate RSA ad text using OpenAI API
    rsa_text = create_rsa_ad_text(keywords)

    # Create an RSA ad
    create_rsa_ad(
        googleads_client,
        customer_id,
        ad_group_id,
        rsa_text,
    )

    print("✅ Campaign, Ad Group, and RSA Ad created successfully!")


if __name__ == "__main__":
    main()