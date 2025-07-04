import feedparser
import requests
from logger_config import get_logger

logger = get_logger("parser_rss")

# from playwright.sync_api import sync_playwright

def parse_rss(url: str) -> list[dict]:
    feed = feedparser.parse(url)
    if feed.entries:
        return [{"title": entry.title, "link": entry.link} for entry in feed.entries]

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return [{"title": entry.title, "link": entry.link} for entry in feed.entries]
    except Exception as e:
        logger.error(f" Ошибка при запросе RSS {url}: {e}")
        return []

def parse_rss(url: str) -> list[dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; Bot/1.0)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return [{"title": entry.title, "link": entry.link} for entry in feed.entries]
    except Exception as e:
        logger.error(f" Ошибка при запросе RSS {url}: {e}")
        return []
    
# def fetch_rss_with_browser(url: str):
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(url)
#         content = page.content()
#         browser.close()
#         return feedparser.parse(content)
#
# feed = fetch_rss_with_browser("https://www.businessoffashion.com/arc/outboundfeeds/rss/?outputType=xml")
# for item in feed.entries:
#     print(item.title, "→", item.link)
