from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import settings as config

bot = Bot(token=config.bot_token)
scheduler = AsyncIOScheduler()
dp = Dispatcher()
