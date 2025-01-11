import pymysql
from config.common import setup_logger, get_config, CONFIG_DIR, ensure_sys_path

# 確保 sys.path 配置正確
ensure_sys_path()

# 初始化日誌
logger = setup_logger(script_name="db_connection")

def connect_db():
    """
    使用配置文件建立並返回 MySQL 數據庫連接。
    """
    try:
        # 從 common.py 獲取數據庫配置信息
        db_config_file = f"{CONFIG_DIR}/database_config.json"
        db_config = {
            "host": get_config("host", json_file=db_config_file),
            "user": get_config("user", json_file=db_config_file),
            "password": get_config("password", json_file=db_config_file),
            "database": get_config("database", json_file=db_config_file),
            "charset": get_config("charset", json_file=db_config_file, default="utf8mb4"),
        }

        # 創建數據庫連接
        connection = pymysql.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
            charset=db_config["charset"],
            cursorclass=pymysql.cursors.DictCursor,  # 返回字典格式的結果
        )
        logger.info("✅ 成功連接到數據庫")
        return connection
    except Exception as e:
        logger.error(f"❌ 連接數據庫失敗: {e}")
        raise

def fetch_keywords_from_database(connection=None, min_searches=100):
    """
    從數據庫中獲取符合條件的關鍵詞。

    Args:
        connection (object, optional): 現有的數據庫連接對象。如果未提供，將自動建立連接。
        min_searches (int, optional): 關鍵詞的最低平均每月搜索量，默認為 100。

    Returns:
        list: 符合條件的關鍵詞列表
    """
    try:
        # 如果沒有提供 connection，自動建立
        if connection is None:
            connection = connect_db()

        with connection.cursor() as cursor:
            query = f"SELECT keyword FROM ecommerce_data_db.keywords WHERE avg_monthly_searches >= %s"
            cursor.execute(query, (min_searches,))
            result = cursor.fetchall()

        keywords = [row["keyword"] for row in result]
        if not keywords:
            logger.warning("⚠️ 關鍵詞列表為空，請檢查數據庫內容。")
        return keywords
    except Exception as e:
        logger.error(f"❌ 無法從數據庫加載關鍵詞: {e}")
        return []
    finally:
        if connection:
            connection.close()
            logger.info("🔒 數據庫連接已關閉")

# 測試代碼
if __name__ == "__main__":
    try:
        logger.info("===== 測試開始 =====")
        conn = connect_db()
        logger.info("數據庫連接成功")

        keywords = fetch_keywords_from_database(conn)
        logger.info(f"加載到的關鍵詞: {keywords}")
    except Exception as e:
        logger.error(f"❌ 測試失敗: {e}")
