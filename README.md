# Threads Media Scraper
這是一個使用 Python + Playwright 製作的工具，能自動擷取 Threads 貼文中的圖片與影片，並下載到本機資料夾。

## ✅ 功能說明
- 自動開啟 Threads 貼文頁面（使用 Chromium）
- 擷取貼文作者名稱與帳號
- 過濾並下載貼文中的圖片與影片（不包含頭像等非內容圖）
- 將圖片與影片依照作者資訊儲存到對應資料夾
- 抓取threads貼文內容的圖片和影片，並爬取發文者帳號名稱資訊

## 🧰 環境需求
- Python 3.7+
- Google Chrome 安裝於預設路徑（或修改路徑）
- 作業系統建議使用 Windows

## 📦 安裝方式
1. 建立虛擬環境（可選）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```
2. 安裝必要套件：
```bash
pip install playwright beautifulsoup4 requests
playwright install chromium
```

## 🚀 使用方式
1. 編輯 `crawler_thread.py`中的 `url` 變數，改成你想要爬取的 Threads 貼文網址：
```python
url = "https://www.threads.net/@username/post/123456789"
```

2. 執行腳本：
```bash
python crawler_thread.py
```

📁 檔案結構
```bash
project/
│
├── crawler_thread.py       # 主程式（即上方程式碼）
├── post_div.html           # 除錯用：抓取的 HTML 片段
├── elements.html           # 除錯用：圖片與影片元素清單
└── downloads/
    └── 作者名稱_帳號/
        ├── image_1.jpg
        ├── image_2.jpg
        └── video_1.mp4

```

## ⚠️ 注意事項
- 若 Threads 更改頁面結構，可能需調整程式碼中的選擇器
- 請勿用於侵犯他人隱私或違反平台政策
- 若出現「❌ 無法解析作者資料」，表示該貼文格式不符目前正則規則
- 爬取的圖片影片會包含一些非貼文的圖片影片

## 🔧 自訂項目
- 修改 `is_valid_media_url` 可調整圖片過濾邏輯
- 修改 `extract_media_urls` 中的選擇器支援不同語言/版型
- 更換 `browser.executable_path` 為你本地的 Chromium 或 Chrome 路徑

