from modules.database.db_connection import connect_db
from modules.api.google_ads_api import load_google_ads_client, generate_keyword_ideas


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


def chunk_keywords(keywords, chunk_size=20):
    """
    將關鍵字列表切割為大小為chunk_size的小批量。
    """
    for i in range(0, len(keywords), chunk_size):
        yield keywords[i:i + chunk_size]


def insert_new_keywords_to_table(table_name, keywords_data):
    """
    檢查關鍵字是否存在，僅插入新的關鍵字，跳過更新現有的關鍵字。
    """
    try:
        connection = connect_db()  # 使用 db_connection.py 的連接方法
        with connection.cursor() as cursor:
            for data in keywords_data:
                # 檢查關鍵字是否已存在
                cursor.execute(f"SELECT * FROM {table_name} WHERE keyword = %s", (data["text"],))
                existing_keyword = cursor.fetchone()

                if existing_keyword:
                    # 如果關鍵字已存在，則跳過
                    print(f"❌ 關鍵字已存在，跳過: {data['text']}")
                else:
                    # 如果關鍵字不存在，則插入
                    cursor.execute(
                        f"""
                        INSERT INTO {table_name} (keyword, avg_monthly_searches, competition_level) 
                        VALUES (%s, %s, %s)
                        """,
                        (data["text"], data["avg_monthly_searches"], data["competition"])
                    )
                    print(f"✅ 插入關鍵字: {data['text']}")
            
        connection.commit()
        connection.close()
        print(f"✅ 關鍵字數據操作完成！")
    except Exception as e:
        print(f"❌ 無法操作關鍵字數據到 MySQL：{e}")
        raise


def main():
    # 配置 MySQL 表名
    keyword_table = "keywords"

    # 加載 Google Ads 客戶端
    client = load_google_ads_client()

    # 1. 從 MySQL 獲取關鍵字列表
    keywords = fetch_keywords_from_table(keyword_table)

    # 2. 將關鍵字分成 20 個一組的小批量
    keyword_batches = chunk_keywords(keywords, 20)

    # 3. 逐批處理關鍵字
    for batch in keyword_batches:
        # 使用 Google Ads API 生成篩選後的關鍵字建議
        keyword_results = generate_keyword_ideas(
            client=client,
            customer_id="5141511711",
            location_ids=["2840"],  # 示例地區 ID (美國)
            language_id="1000",  # 示例語言 ID (英語)
            keyword_texts=batch,
            page_url=None
        )

        # 4. 將生成的數據插入到 MySQL 表中（不更新現有數據）
        insert_new_keywords_to_table(keyword_table, keyword_results)

    print("✅ 整個工作流執行完成！")


if __name__ == "__main__":
    main()