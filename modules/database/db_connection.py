import json
import pymysql
import os

# 獲取項目根目錄路徑
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_CONFIG_PATH = os.path.join(BASE_DIR, "config", "db_config.json")

def load_db_config():
    """
    從 db_config.json 文件中加載數據庫配置信息。
    """
    try:
        with open(DB_CONFIG_PATH, "r") as file:
            config = json.load(file)
            return config
    except FileNotFoundError:
        print(f"未找到數據庫配置文件: {DB_CONFIG_PATH}")
        raise
    except json.JSONDecodeError as e:
        print(f"數據庫配置文件格式錯誤: {e}")
        raise
    except Exception as e:
        print(f"無法加載數據庫配置: {e}")
        raise

def connect_db():
    """
    使用 db_config.json 中的配置信息建立並返回 MySQL 數據庫連接。
    """
    try:
        db_config = load_db_config()  # 加載數據庫配置
        connection = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            charset=db_config.get("charset", "utf8mb4"),  # 默認使用 utf8mb4
            cursorclass=pymysql.cursors.DictCursor,  # 返回字典格式的結果
        )
        print("成功連接到數據庫")
        return connection
    except Exception as e:
        print(f"連接數據庫失敗: {e}")
        raise

def fetch_keywords_from_database(connection=None):
    """
    從數據庫中獲取關鍵詞，並只選擇 avg_monthly_searches >= 100 的關鍵字。

    Args:
        connection (object, optional): 現有的數據庫連接對象。如果未提供，將自動建立連接。

    Returns:
        list: 關鍵詞列表。
    """
    try:
        # 如果沒有提供 connection，自動建立
        if connection is None:
            connection = connect_db()

        cursor = connection.cursor()
        # 加入條件：選擇 avg_monthly_searches >= 100 的關鍵字
        cursor.execute("SELECT keyword FROM ecommerce_data_db.keywords WHERE avg_monthly_searches >= 100")
        result = cursor.fetchall()
        
        # 確保游標和連接在最後被關閉
        cursor.close()
        if connection:
            connection.close()

        # 提取關鍵詞為列表
        keywords = [row["keyword"] for row in result]
        if not keywords:
            print("關鍵詞列表為空，請檢查數據庫內容。")
        return keywords
    except Exception as e:
        print(f"無法從數據庫加載關鍵詞: {e}")
        return []


# 測試代碼 (僅在直接執行此文件時運行)
if __name__ == "__main__":
    try:
        conn = connect_db()
        conn.close()
        print("數據庫連接測試成功並已關閉")
    except Exception as e:
        print(f"數據庫連接測試失敗: {e}")

