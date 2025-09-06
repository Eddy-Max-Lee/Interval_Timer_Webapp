#!/bin/bash

echo
echo "?? 啟動 Interval Timer MVP 專案（Linux）"
echo "=========================================="

# 切換至腳本所在目錄
cd "$(dirname "$0")"

# Step 1: 確保 Python3 存在
if ! command -v python3 &>/dev/null; then
  echo "? 請先安裝 Python3"
  exit 1
fi

# Step 2: 檢查 pip
if ! command -v pip3 &>/dev/null; then
  echo "? pip3 未安裝，請先安裝 pip"
  exit 1
fi

# Step 3: 安裝 requirements.txt 內套件（僅第一次需要）
echo "?? 安裝 Python 依賴（requirements.txt）..."
pip3 install -r requirements.txt

# Step 4: 執行遷移（如果是初次部署）
echo "?? 執行 Django 資料庫遷移..."
# python3 manage.py makemigrations timers
# python3 manage.py migrate

# Step 5: 啟動伺服器
echo "?? 啟動 Django 伺服器：http://0.0.0.0:8000"
# python3 manage.py runserver 0.0.0.0:8000

gunicorn intervaltimer.wsgi:application --bind 0.0.0.0:8000

