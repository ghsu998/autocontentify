#!/bin/bash

# 提示用戶輸入提交信息
echo "Enter commit message: "
read commit_message

# 檢查是否有變更需要添加
if [ -n "$(git status --porcelain)" ]; then
    # 添加所有變更到暫存區
    git add .

    # 提交到本地倉庫
    git commit -m "$commit_message"

    # 推送到遠端倉庫
    git push origin main

    echo "Changes have been pushed to GitHub!"
else
    echo "No changes to commit."
fi
