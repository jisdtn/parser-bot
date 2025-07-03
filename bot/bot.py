import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import Command
import asyncpg
from typing import Optional
import logging


load_dotenv()



bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
router = Router()

DATABASE_URL = "postgresql://postgres:postgres@db:5432/postgres"

async def get_pool() -> asyncpg.pool.Pool:
    return await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)

pool: Optional[asyncpg.pool.Pool] = None

@router.message(Command("start"))
async def start_handler(message: Message):
    chat_id = message.chat.id

    try:
        async with pool.acquire() as conn:
            await conn.execute("INSERT INTO users (chat_id) VALUES ($1) ON CONFLICT DO NOTHING", chat_id)
    except Exception as e:
        logging.error(f"Не удалось сохранить chat_id: {e}")

    await message.answer("Привет! Когда появятся новые статьи, я их пришлю.")



async def main():
    global pool
    if pool is None:
        pool = await get_pool()
    dp.include_router(router)
    await dp.start_polling(bot)


logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


if __name__ == "__main__":
    asyncio.run(main())
