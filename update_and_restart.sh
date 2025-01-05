#!/bin/bash

# 更新系統
apt update -y
apt upgrade -y

# 進入項目目錄
cd /var/www/autocontentify

# 從 Git 拉取最新代碼
git fetch origin main
git reset --hard origin/main

# 確保虛擬環境存在並激活
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 安裝依賴
pip install --upgrade pip
pip install -r requirements.txt

# 檢查是否存在主程序文件
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py 文件不存在，無法啟動程序！"
    exit 1
fi

# 重啟程序
pkill -f "python3 app.py"
nohup python3 app.py > logs/app.log 2>&1 &
echo "程序已啟動並運行！"
