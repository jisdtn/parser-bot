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
        "title_selector": "h3",
        "link_selector": "a",
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
    "style.rbc.ru": [
    {
        "item_selector": ".itbg_medium",
        "title_selector": ".itbg_medium__text-block__center",
        "link_selector": ".itbg_medium__link",
        "link_attr": "href",
        "base_url": "https://style.rbc.ru"
    },
    {
        "item_selector": ".itlg_main",
        "title_selector": ".itlg_main__title",
        "link_selector": ".itlg_main__link",
        "link_attr": "href",
        "base_url": "https://style.rbc.ru"
    },
    {
        "item_selector": ".itmd_main",
        "title_selector": ".itmd_main__title",
        "link_selector": ".itmd_main__link",
        "link_attr": "href",
        "base_url": "https://style.rbc.ru"
    }
]

}

BS_ONLY_SITES = {
    "instyle.com",
    "showstudio.com",
    "theimpression.com",
    "buro247.ru",
    "style.rbc.ru",
    }


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
    results = []
    browser = None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle")

            if config.get("item_selector"):
                try:
                    await page.wait_for_selector(config["item_selector"], timeout=10000)
                except:
                    print(f"Элементы по селектору {config['item_selector']} не найдены")
                    return []

            items = await page.locator(config["item_selector"]).all()
            for item in items:
                try:
                    if config.get("title_selector"):
                        title_el = item.locator(config["title_selector"])
                        title = await title_el.text_content()
                    else:
                        title = await item.inner_text()
                    if not title:
                        continue

                    link_el = item.locator(
                        config.get("link_selector", config.get("title_selector"))
                    ) if config.get("link_selector") or config.get("title_selector") else item
                    link_attr = config.get("link_attr", "href")
                    link = await link_el.get_attribute(link_attr)
                    if not link:
                        continue

                    if link.startswith("/"):
                        link = config["base_url"].rstrip("/") + link
                    results.append({
                        "title": title.strip(),
                        "link": link.strip()
                    })
                except Exception as e:
                    print(f"Ошибка в элементе: {e}")
                    continue

    except Exception as e:
        print(f"Ошибка в Playwright: {e}")

    finally:
        if browser:
            await browser.close()

    return results



async def try_bs_then_playwright(url):
    domain = get_domain(url)
    config = HTML_SITE_CONFIG.get(domain)
    if not config:
        raise ValueError(f"Нет настроек для домена: {domain}")
    
    config_set = config if isinstance(config, list) else [config]

    print(f"Пробуем BS4 для {url}")
    all_results = []
    for config in config_set:
        results = parse_with_bs4(url, config)
        all_results.extend(results)
    if all_results:
        return all_results

    if domain in BS_ONLY_SITES:
        return []

    print(f"Переключаемся на Playwright для {url}")
    for config in config_set:
        results = await parse_with_playwright(url, config)
        all_results.extend(results)
    return all_results


