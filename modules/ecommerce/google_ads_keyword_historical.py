from modules.database.db_connection import connect_db
from modules.api.google_ads_api import load_google_ads_client, generate_keyword_historical_metrics


def fetch_keywords_from_table(table_name):
    """
    從 MySQL 關鍵字表中讀取關鍵字列表。
    """
    try:
        connection = connect_db()  # 使用 db_connection.py 的連接方法
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT keyword FROM {table_name}")
            keywords = [row["keyword"] for row in cursor.fetchall()]
        connection.close()
        print(f"✅ 從表 {table_name} 中讀取了 {len(keywords)} 條關鍵字。")
        return keywords
    except Exception as e:
        print(f"❌ 無法從 MySQL 獲取關鍵字：{e}")
        raise


def insert_or_update_historical_metrics_to_table(table_name, historical_data):
    """
    Insert or update historical data for keywords into the MySQL table.
    """
    try:
        connection = connect_db()  # Connect to the database
        with connection.cursor() as cursor:
            for data in historical_data:
                # Ensure that all required fields exist, handle missing data
                keyword = data.get("keyword")
                avg_monthly_searches = data.get("avg_monthly_searches", 0)  # Default to 0 if missing
                competition = data.get("competition", "UNKNOWN")  # Default to "UNKNOWN" if missing
                competition_index = data.get("competition_index", 0)  # Default to 0 if missing
                low_bid_range = data.get("low_bid_range", 0) / 1000000  # Convert from micros to normal unit
                high_bid_range = data.get("high_bid_range", 0) / 1000000  # Convert from micros to normal unit
                low_top_of_page_bid_micros = data.get("low_top_of_page_bid_micros", 0)
                high_top_of_page_bid_micros = data.get("high_top_of_page_bid_micros", 0)
                low_top_of_page_bid_percentile = data.get("low_top_of_page_bid_percentile", 0)
                high_top_of_page_bid_percentile = data.get("high_top_of_page_bid_percentile", 0)

                # Check if the keyword already exists in the table
                cursor.execute(f"SELECT * FROM {table_name} WHERE keyword = %s", (keyword,))
                existing_keyword = cursor.fetchone()

                if existing_keyword:
                    # Update the existing record with new data
                    cursor.execute(
                        f"""
                        UPDATE {table_name} 
                        SET avg_monthly_searches = %s, competition_level = %s, 
                            competition_index = %s, low_bid_range = %s, high_bid_range = %s,
                            low_top_of_page_bid_micros = %s, high_top_of_page_bid_micros = %s, 
                            low_top_of_page_bid_percentile = %s, high_top_of_page_bid_percentile = %s
                        WHERE keyword = %s
                        """,
                        (
                            avg_monthly_searches, 
                            competition, 
                            competition_index, 
                            low_bid_range, 
                            high_bid_range,
                            low_top_of_page_bid_micros, 
                            high_top_of_page_bid_micros,
                            low_top_of_page_bid_percentile, 
                            high_top_of_page_bid_percentile,
                            keyword
                        )
                    )
                    print(f"✅ Updated keyword: {keyword}")
                else:
                    # Insert a new record if the keyword does not exist
                    cursor.execute(
                        f"""
                        INSERT INTO {table_name} (keyword, avg_monthly_searches, competition_level, 
                        competition_index, low_bid_range, high_bid_range,
                        low_top_of_page_bid_micros, high_top_of_page_bid_micros, 
                        low_top_of_page_bid_percentile, high_top_of_page_bid_percentile) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            keyword, 
                            avg_monthly_searches, 
                            competition, 
                            competition_index, 
                            low_bid_range, 
                            high_bid_range,
                            low_top_of_page_bid_micros, 
                            high_top_of_page_bid_micros,
                            low_top_of_page_bid_percentile, 
                            high_top_of_page_bid_percentile
                        )
                    )
                    print(f"✅ Inserted keyword: {keyword}")
            
        connection.commit()
        connection.close()
        print(f"✅ Historical data operation completed successfully!")
    except Exception as e:
        print(f"❌ Failed to operate on historical keyword data in MySQL: {e}")
        raise


def main():
    # 配置 MySQL 表名
    keyword_table = "keywords"

    # 加載 Google Ads 客戶端
    client = load_google_ads_client()

    # 1. 從 MySQL 獲取關鍵字列表
    keywords = fetch_keywords_from_table(keyword_table)

    # 2. 使用 Google Ads API 獲取關鍵字的歷史數據
    historical_data = generate_keyword_historical_metrics(
        client=client,
        customer_id="5141511711",
        keywords=keywords
    )

    # 3. 將歷史數據插入或更新到 MySQL 表中
    insert_or_update_historical_metrics_to_table(keyword_table, historical_data)
    print("✅ 整個工作流執行完成！")


if __name__ == "__main__":
    main()