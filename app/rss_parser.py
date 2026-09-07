import feedparser
import requests
from logger_config import get_logger

logger = get_logger("parser_rss")


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
