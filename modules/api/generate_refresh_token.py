from google_auth_oauthlib.flow import InstalledAppFlow
import os
import pickle
from dotenv import load_dotenv

# 動態設置 BASE_DIR
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))

# 指定憑據文件
CLIENT_SECRETS_FILE = os.path.join(BASE_DIR, "config", "google_ads_credentials.json")

def generate_refresh_token():
    # 確保憑據文件存在
    if not os.path.exists(CLIENT_SECRETS_FILE):
        raise FileNotFoundError(f"❌ 憑據文件未找到: {CLIENT_SECRETS_FILE}")
    
    print(f"正在使用憑據文件: {CLIENT_SECRETS_FILE}")
    
    # 設置 OAuth 範圍
    SCOPES = ["https://www.googleapis.com/auth/adwords"]

    # 啟動 OAuth 流程
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)

    # 添加 access_type='offline' 以獲取 refresh token
    credentials = flow.run_local_server(port=53921, access_type='offline')

    # 打印 Access Token 和 Refresh Token
    print("Access Token:", credentials.token)
    print("Refresh Token:", credentials.refresh_token)
    print("Client ID:", credentials.client_id)
    print("Client Secret:", credentials.client_secret)

    # 保存憑據（可選）
    if credentials.refresh_token:
        with open("credentials.pickle", "wb") as token:
            pickle.dump(credentials, token)

if __name__ == "__main__":
    # 執行刷新 Token 的函數
    generate_refresh_token()
