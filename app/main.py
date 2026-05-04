import asyncio

from aiogram import Bot, Dispatcher, types

from app.config import settings as config
from app.handlers import router


BOT_TOKEN = config.bot_token


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

