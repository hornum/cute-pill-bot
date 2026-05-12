from aiogram import F, Router

from aiogram.types import CallbackQuery
from datetime import datetime, timedelta, timezone
from app.bot.instance import bot, scheduler
from app.scheduler.jobs import resend_reminder

router = Router()

@router.callback_query(F.data.startswith("taken:"))
async def on_taken(callback: CallbackQuery):
    await callback.message.edit_text("✅ Приём отмечен!")
    await callback.answer()

@router.callback_query(F.data.startswith("skipped:"))
async def on_skipped(callback: CallbackQuery):
    await callback.message.edit_text("❌ Приём пропущен.")
    await callback.answer()

@router.callback_query(F.data.startswith("snooze:"))
async def on_snooze(callback: CallbackQuery):
    reminder_id = int(callback.data.split(":")[1])
    snooze_time = datetime.now(timezone.utc) + timedelta(minutes=15)

    scheduler.add_job(
        resend_reminder,
        trigger="date",
        run_date=snooze_time,
        args=[bot, callback.message.chat.id, reminder_id],
    )

    await callback.message.edit_text("⏰ Напомню через 15 минут!")
    await callback.answer()

