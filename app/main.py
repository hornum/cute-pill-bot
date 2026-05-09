import asyncio

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings as config
from app.config import CHECK_REMINDERS_INTERVAL_SECS as CHECK_INTERVAL
from app.bot.handlers import router
from app.scheduler.jobs import check_reminders

BOT_TOKEN = config.bot_token


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def main() -> None:
    dp.include_router(router)

    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_reminders,
        "interval",
        seconds=CHECK_INTERVAL,
        args=[bot],
    )

    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

