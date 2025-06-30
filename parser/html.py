from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright


HTML_SITE_CONFIG = {
    "instyle.com": {
        "item_selector": "a.mntl-card-list-items",
        "title_selector": "span.card__title-text",
        "link_attr": "href",
        "base_url": "https://www.instyle.com"

    },
    "showstudio.com": {
        "item_selector": "a.block",           # ??????
        "title_selector": "h3",
        "link_attr": "href",
        "base_url": "https://www.showstudio.com",

    },
    "theimpression.com": {
        "item_selector": "article.tipi-xs-12",
        "title_selector": "h3 a",
        "link_selector": "h3 a",
        "link_attr": "href",
        "base_url": "https://theimpression.com",

    },
    "system-magazine.com": {
        "item_selector": "div.articles-item.text-center.has-image",   # ???????
        "title_selector": "div.articles-item__title",
        "link_selector": "a.block--link",
        "link_attr": "href",
        "base_url": "https://system-magazine.com",

    },
    "buro247.ru": {
        "item_selector": "article.mb-60.regular, div.top-five__item.slick-slide",
        "title_selector": "h4.link-text, h2",
        "link_selector": "a.no-underline, a[href^='/']",
        "link_attr": "href",
        "base_url": "https://www.buro247.ru"

    },
    "style.rbc.ru": {
        "item_selector": "div[itemtype='https://schema.org/NewsArticle']",       # ??????
        "title_selector": "span[itemprop='headline']",
        "link_selector": "a[itemprop='url']",
        "link_attr": "href",
        "base_url": "https://style.rbc.ru"
    }

}

BS_ONLY_SITES = {"instyle.com"}


def get_domain(url):
    return urlparse(url).netloc.replace("www.", "")


def parse_with_bs4(url, config):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.select(config["item_selector"])
        results = []

        for item in items:
            title_el = item.select_one(config["title_selector"])
            if not title_el:
                continue
            title = title_el.get_text(strip=True)

            if config.get("link_selector"):
                link_el = item.select_one(config["link_selector"])
            else:
                link_el = item

            if not link_el:
                continue

            link = link_el.get(config["link_attr"])
            if not link:
                continue
            if link and link.startswith("/"):
                link = config["base_url"] + link

            results.append({"title": title, "link": link})

        return results
    except Exception as e:
        print(f"BS4 парсинг не удался: {e}")
        return []



async def parse_with_playwright(url, config):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, timeout=30000)
        await page.wait_for_load_state("networkidle")

        items = await page.locator(config["item_selector"]).all()
        results = []
        for item in items:
            try:
                if config.get("title_selector"):
                    title_el = item.locator(config["title_selector"])
                    title = await title_el.text_content()
                else:
                    title = await item.inner_text()

                link_el = item.locator(config.get("link_selector", config["title_selector"])) if config.get("link_selector") else item
                link = await link_el.get_attribute(config["link_attr"])

                if title and link:
                    if link.startswith("/"):
                        link = config["base_url"] + link
                    results.append({"title": title.strip(), "link": link.strip()})
            except Exception as e:
                print(f"Ошибка в элементе: {e}")
                continue
        await browser.close()
        return results



async def try_bs_then_playwright(url):
    domain = get_domain(url)
    config = HTML_SITE_CONFIG.get(domain)
    if not config:
        raise ValueError(f"Нет настроек для домена: {domain}")

    print(f"Пробуем BS4 для {url}")
    results = parse_with_bs4(url, config)
    if results or domain in BS_ONLY_SITES:
        return results

    print(f"Переключаемся на Playwright для {url}")
    return await parse_with_playwright(url, config)

