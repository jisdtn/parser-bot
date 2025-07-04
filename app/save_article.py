from aiogram import Bot
from typing import List, Dict
import asyncpg
from logger_config import get_logger

logger = get_logger("save_article")


async def save_new_articles_and_notify(pool: asyncpg.pool.Pool, articles: List[Dict], bot: Bot):
    async with pool.acquire() as conn:
        chat_ids = await conn.fetch("SELECT chat_id FROM users")
        for article in articles:
            try:
                title = article["title"]
                link = article["link"]

                existing = await conn.fetchval("SELECT 1 FROM articles WHERE link = $1", link)
                if existing:
                    continue

                await conn.execute(
                    "INSERT INTO articles (title, link) VALUES ($1, $2)",
                    title, link
                )

                msg = f"Обновки: {title}\n{link}"
                for record in chat_ids:
                    try:
                        await bot.send_message(chat_id=record["chat_id"], text=msg)
                    except Exception as e:
                        logger.error(f"Не удалось отправить сообщение {record['chat_id']}: {e}")

            except Exception as e:
                logger.error(f"Ошибка при обработке статьи {article}: {e}")
