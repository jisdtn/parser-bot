from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from fastapi import FastAPI
import asyncio
import os
from urls import rss_urls, html_urls
from parser.rss import parse_rss
from parser.html import try_bs_then_playwright

from dotenv import load_dotenv
load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
router = Router()

app = FastAPI()

@app.on_event("startup")
async def startup():
    print("Парсим RSS источники:")
    for url in rss_urls:
        print(f"\n--- {url} ---")
        try:
            for item in parse_rss(url):
                print(f"{item['title']} → {item['link']}")
        except Exception as e:
            print(f"Ошибка при парсинге RSS {url}: {e}")

    for url in html_urls:
        try:
            print(f"\n--- {url} ---")
            results = await try_bs_then_playwright(url)
            if not results:
                print("Ничего не найдено.")
            for item in results:
                print(f"{item['title']} → {item['link']}")
        except Exception as e:
            print(f" Ошибка для {url}: {e}")


@app.get("/")
def root():
    return {"message": "Парсинг при старте выполнен, проверь терминал."}


# сначала проверить, что все парсится нормально

# сохранение результата парсинга в бд (подключить бд)

# скрипт, который использует методы для хтмл и рсс и проверяет совпадения записей в бд и на сайте ресурса

# отправка ботом новых записей пользователю

# упаковать все в контейнеры
