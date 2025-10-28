"""
map_generator.py
新しいSentinel-2画像（雲量20％以下）があればマップを自動更新し、GitHub Pagesにpush
"""

import ee
import os
from datetime import datetime
import subprocess

# ==== Earth Engine 初期化（認証トークンはActionsで設定済み） ====
ee.Initialize()

# ==== 設定 ====
GITHUB_USER = "kitsukisaiseikyo-byte"
REPO_NAME = "shinjo-mugimap"
BRANCH = "main"
OUTPUT_HTML = "index.html"
LATEST_FILE = "latest_date.txt"
COMMIT_MESSAGE = f"auto update map {datetime.now():%Y-%m-%d %H:%M:%S}"

# ==== 解析対象範囲 ====
boundary = ee.Geometry.Polygon([
    [131.388245, 33.554557],
    [131.773453, 33.576871],
    [131.772766, 33.353473],
    [131.384811, 33.350606],
    [131.388245, 33.554557]
])

# ==== Sentinel-2 最新画像チェック ====
print("🔍 新しい画像をチェック中...")
collection = (
    ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(boundary)
    .filterDate('2025-01-01', datetime.now().strftime('%Y-%m-%d'))
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    .sort('system:time_start', False)
)

latest_image = collection.first()
latest_date = ee.Date(latest_image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
print(f"最新観測日: {latest_date}")

# ==== 前回日付との比較 ====
if os.path.exists(LATEST_FILE):
    with open(LATEST_FILE, 'r') as f:
        last_date = f.read().strip()
else:
    last_date = None

if last_date == latest_date:
    print("✅ 新しい画像はありません。終了します。")
    exit(0)

print("🛰️ 新しい画像があります！マップを生成します。")

# ==== マップ生成（ここを既存のマップ処理に差し替え）====
with open(OUTPUT_HTML, "w") as f:
    f.write(f"<html><body><h2>新しいマップ: {latest_date}</h2></body></html>")

# ==== 日付更新 ====
with open(LATEST_FILE, 'w') as f:
    f.write(latest_date)

# ==== Git操作 ====
subprocess.run(["git", "config", "--global", "user.name", "auto-bot"])
subprocess.run(["git", "config", "--global", "user.email", "auto@bot.com"])
subprocess.run(["git", "add", "."])
subprocess.run(["git", "commit", "-m", COMMIT_MESSAGE])
subprocess.run(["git", "push", "origin", BRANCH])

print("✅ GitHub Pagesへ自動反映完了！")

