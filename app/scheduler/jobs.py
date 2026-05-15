from datetime import datetime, timezone, time

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.bot.keyboards import pill_confirmation
from app.db.models import Reminder, Medicine
from app.db.session import async_session_maker


def get_time_without_secs() -> time:
    now = datetime.now()
    now = now.time().replace(second=0, microsecond=0)
    return now


def was_send_today(last_sent_at: datetime | None) -> bool:
    if last_sent_at is None:
        return False

    now = datetime.now()
    return now.date() == last_sent_at.date()


async def send_reminder(bot: Bot, chat_id: int, reminder: Reminder) -> None:

    if reminder is None:
        return

    await bot.send_message(
        chat_id=chat_id,
        text=(
            "Напоминание\n"
            f"Пора принять {reminder.medicine.name}\n"
            f"В количестве: {reminder.medicine.dosage}\n"
        ),
        reply_markup=pill_confirmation(reminder.id)
    )


async def resend_reminder(bot: Bot, chat_id: int, reminder_id: int):
    async with async_session_maker() as session:
        query = (
            select(Reminder)
            .options(joinedload(Reminder.medicine))
            .where(Reminder.id == reminder_id)
        )
        result = await session.execute(query)
        reminder = result.scalar_one_or_none()

        await send_reminder(bot, chat_id, reminder)


async def check_reminders(bot: Bot) -> None:
    current_time = get_time_without_secs()

    async with async_session_maker() as session:
        query = (
            select(Reminder)
            .options(joinedload(Reminder.medicine).joinedload(Medicine.user)
                     ).where(
                Reminder.reminder_time == current_time,
                Reminder.is_active == True,
            )
        )

        result = await session.execute(query)
        reminders = result.scalars().all()

        for reminder in reminders:
            if was_send_today(reminder.last_sent_at):
                continue

            medicine = reminder.medicine
            user = medicine.user

            await send_reminder(bot, user.chat_id, reminder)

            reminder.last_sent_at = datetime.now(timezone.utc)

        await session.commit()
