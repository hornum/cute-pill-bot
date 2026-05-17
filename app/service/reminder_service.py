from datetime import time, datetime

from sqlalchemy import delete

from app.db.models import Reminder
from app.db.session import async_session_maker


def parse_reminder_time(time_to_remind: str) -> time:
    try:
        return datetime.strptime(time_to_remind, "%H:%M").time()
    except ValueError:
        raise ValueError(f"Время должно быть указано в формате ЧЧ:ММ, например 09:30")

def get_time_without_sec(time_to_remind: time) -> str:
    return time_to_remind.strftime("%H:%M")


async def delete_all_reminders(med_id: int) -> None:
    async with async_session_maker() as session:
        await session.execute(
            delete(Reminder).where(Reminder.medicine_id == med_id)
        )
        await session.commit()


async def add_reminders_to_medicine(med_id: int, times: list[str]) -> list[Reminder]:
    async with async_session_maker() as session:
        reminders = []

        for str_time in times:
            reminder = Reminder(
                medicine_id=med_id,
                reminder_time=parse_reminder_time(str_time)
            )
            session.add(reminder)
            reminders.append(reminder)

        await session.commit()
        return reminders
