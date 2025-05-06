import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import os
import re
import requests
from urllib.parse import urlparse


def is_valid_media_url(url):
    """用來過濾非貼文內容的圖（像頭像）"""
    return re.search(r"instagram.*(fbcdn\.net|cdninstagram\.com)", url) and (
        re.search(r"\.jpg|\.jpeg|\.png|\.mp4", url)
    )

def get_post_author(html):
    """取得貼文作者的名稱與帳號"""
    soup = BeautifulSoup(html, "html.parser")
    meta = soup.find("meta", {"name": "twitter:title"})
    print("get_post_author:", meta)
    if not meta:
        return None, None

    content = meta.get("content", "")
    match = re.search(r"Threads 上的(.+?)（(@[^）]+)）", content)
    if match:
        return match.group(1), match.group(2)
    match = re.search(r"(.+?)\s+\((@[^)]+)\)\s+on Threads", content)
    if match:
        return match.group(1), match.group(2)
    return None, None

async def extract_media_urls(page):
    """擷取貼文內所有的圖片與影片 URL"""
    # 抓取文章內的圖片與影片元素
    # post_div = page.locator("div[aria-label='直欄內文'] > div").first
    post_divs = page.locator("div[aria-label='直欄內文'] > div")
    post_div = post_divs.nth(0)
    with open("post_div.html", "w", encoding="utf-8") as f:
        f.write(await post_div.inner_html())
    img_elements = await post_div.locator("img[src]:not([alt*='大頭貼照'])").all()
    video_elements = await post_div.locator("video[src]").all()

    image_urls = set()
    video_urls = set()

    # 儲存圖片 HTML
    with open("elements.html", "w", encoding="utf-8") as f:
        for i, img in enumerate(img_elements):
            src = await img.get_attribute("src")
            if src and is_valid_media_url(src):
                image_urls.add(src)
                outer_html = await img.evaluate("e => e.outerHTML")
                f.write(f"{i+1}: {src}\n{outer_html}\n\n")
        for i, video in enumerate(video_elements):
            src = await video.get_attribute("src")
            if src and is_valid_media_url(src):
                video_urls.add(src)
                outer_html = await video.evaluate("e => e.outerHTML")
                f.write(f"{i+1}: {src}\n{outer_html}\n\n")
    return list(image_urls), list(video_urls)

async def scrape_threads_post(post_url, download_folder="downloads"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe"
            )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            bypass_csp=True,
        )
        page = await context.new_page()
        await page.goto(post_url, wait_until="domcontentloaded")

        await page.wait_for_selector("body", timeout=10000)
        
        html = await page.content()

        # 擷取作者資訊
        realname, username = get_post_author(html)
        if not realname or not username:
            print("❌ 無法解析作者資料")
            return
        
        print(f"👤 作者：{realname}（{username}）")

        # 設定儲存資料夾
        save_dir = os.path.join(download_folder, f"{realname}_{username}")
        os.makedirs(save_dir, exist_ok=True)

        # input("按 Enter 鍵繼續...")

        image_urls, video_urls = await extract_media_urls(page)
        print(f"📸 圖片數：{len(image_urls)}")
        print(f"🎥 影片數：{len(video_urls)}")

        # 下載圖片
        for i, url in enumerate(image_urls):
            ext = os.path.splitext(urlparse(url).path)[-1].split("?")[0] or ".jpg"
            filename = f"image_{i+1}{ext}"
            filepath = os.path.join(save_dir, filename)
            try:
                with open(filepath, "wb") as f:
                    f.write(requests.get(url).content)
                print(f"✅ 已下載圖片：{filename}")
            except Exception as e:
                print(f"❌ 圖片下載失敗 {url}: {e}")

        # 下載影片
        for i, url in enumerate(video_urls):
            ext = os.path.splitext(urlparse(url).path)[-1].split("?")[0] or ".mp4"
            filename = f"video_{i+1}{ext}"
            filepath = os.path.join(save_dir, filename)
            try:
                with open(filepath, "wb") as f:
                    f.write(requests.get(url).content)
                print(f"✅ 已下載影片：{filename}")
            except Exception as e:
                print(f"❌ 影片下載失敗 {url}: {e}")

        await browser.close()


if __name__ == "__main__":
    url = "要爬取的threads貼文網址"
    asyncio.run(scrape_threads_post(url))
