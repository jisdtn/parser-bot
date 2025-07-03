import os
import logging
from html_parser import try_bs_then_playwright
from rss_parser import parse_rss
from typing import Optional
from aiogram import Bot

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI

from urls import html_urls, rss_urls
from save_article import save_new_articles_and_notify

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
app = FastAPI()

DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"

async def get_pool() -> asyncpg.pool.Pool:
    return await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)

pool: Optional[asyncpg.pool.Pool] = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await get_pool()
    await parse_sources()

@app.on_event("shutdown")
async def shutdown():
    await pool.close()


async def parse_sources():
    logging.info("Парсим RSS источники:")
    
    for url in rss_urls:
        logging.info(f"\n--- {url} ---")
        try:
            for item in parse_rss(url):
                await save_new_articles_and_notify(pool, [item], bot)
                logging.info(f"{item['title']} → {item['link']}")
        
        except Exception as e:
            logging.error(f"Ошибка при парсинге RSS {url}: {e}")

    logging.info("Парсим HTML источники:")
    for url in html_urls:
        try:
            logging.info(f"\n--- {url} ---")
            results = await try_bs_then_playwright(url)
            if not results:
                logging.error("Ничего не найдено.")
            for item in results:
                logging.info(f"{item['title']} → {item['link']}")

            await save_new_articles_and_notify(pool, results, bot)

        except Exception as e:
            logging.error(f" Ошибка для {url}: {e}")


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# business of fashion и system_magazine - нужно разобраться и поключить их тоже



# отправка ботом новых записей пользователю


# осталось проверить: 

# - как работает сравнение, точно ли новые сохраняются
# - сообщение с новыми уходит пользователю 

# сообщения не ушли пользователю