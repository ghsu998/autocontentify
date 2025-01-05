# AutoContentify/
# ├── config/
# │   ├── common.py
# │   ├── google_ads_credentials.json
# │   ├── google_ads.yaml
# ├── modules/
# │   ├── api/
# │   ├── database/
# │   ├── ecommerce/
# ├── logs/



import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# 設置項目根目錄
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# 設置其他重要目錄
CONFIG_DIR = os.path.join(BASE_DIR, "config")
MODULES_DIR = os.path.join(BASE_DIR, "modules")
LOG_DIR = os.path.join(BASE_DIR, "logs")

API_DIR = os.path.join(MODULES_DIR, "api")
DATABASE_DIR = os.path.join(MODULES_DIR, "database")
ECOMMERCE_DIR = os.path.join(MODULES_DIR, "ecommerce")

# 確保日誌目錄存在
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def setup_logger(script_name=None, log_dir=LOG_DIR, log_level=logging.INFO):
    """
    配置並返回一個動態的日誌記錄器。

    Args:
        script_name (str): 運行的腳本名稱，若為 None，則根據 sys.argv[0] 動態獲取。
        log_dir (str): 日誌存放的目錄，默認為 LOG_DIR。
        log_level (int): 日誌級別，默認為 logging.INFO。

    Returns:
        logging.Logger: 配置好的日誌記錄器。
    """
    # 獲取腳本名稱，默認使用運行的 .py 文件名稱
    if script_name is None:
        script_name = os.path.basename(sys.argv[0]).replace(".py", "")
    log_file = os.path.join(log_dir, f"{script_name}.log")

    # 創建記錄器
    logger = logging.getLogger(script_name)
    if not logger.hasHandlers():
        rotating_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
        rotating_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
        ))

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s"
        ))

        logger.setLevel(log_level)
        logger.addHandler(rotating_handler)
        logger.addHandler(stream_handler)

        # 初始化信息
        logger.info("日誌系統已初始化，日誌輸出文件: %s", log_file)

    return logger


if __name__ == "__main__":
    # 測試日誌初始化
    logger = setup_logger()
    logger.info("======== 新的運行開始 ========")
    print(f"BASE_DIR: {BASE_DIR}")
    print(f"CONFIG_DIR: {CONFIG_DIR}")
    print(f"LOG_DIR: {LOG_DIR} -> {'存在' if os.path.exists(LOG_DIR) else '不存在'}")
    print(f"CONFIG_DIR: {CONFIG_DIR} -> {'存在' if os.path.exists(CONFIG_DIR) else '不存在'}")
    print(f"MODULES_DIR: {MODULES_DIR} -> {'存在' if os.path.exists(MODULES_DIR) else '不存在'}")
    print(f"API_DIR: {API_DIR} -> {'存在' if os.path.exists(API_DIR) else '不存在'}")
    print(f"DATABASE_DIR: {DATABASE_DIR} -> {'存在' if os.path.exists(DATABASE_DIR) else '不存在'}")
    print(f"ECOMMERCE_DIR: {ECOMMERCE_DIR} -> {'存在' if os.path.exists(ECOMMERCE_DIR) else '不存在'}")
    