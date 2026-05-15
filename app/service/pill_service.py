from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.models import Medicine, Reminder
from app.db.session import async_session_maker
from app.service.reminder_service import parse_reminder_time
from app.service.user_service import get_user_or_raise


async def create_medicine_and_reminder(
        tg_id: int,
        pill_name: str,
        dose: str,
        str_time: str
) -> Medicine:

    parsed_time = parse_reminder_time(str_time)

    async with async_session_maker() as session:

        user = await get_user_or_raise(tg_id=tg_id)

        medicine = Medicine(
            user_id = user.id,
            name = pill_name,
            dosage = dose
        )
        session.add(medicine)
        await session.flush()

        reminder = Reminder(
            medicine_id = medicine.id,
            reminder_time = parsed_time
        )
        session.add(reminder)

        await session.commit()
        await session.refresh(medicine)

        return medicine

async def get_medicines_and_reminders_list(tg_id: int) -> list:
    user = await get_user_or_raise(tg_id=tg_id)

    async with async_session_maker() as session:
        query = (
            select(Medicine)
            .options(joinedload(Medicine.reminders))
            .where(Medicine.user_id == user.id)
        )
        result = await session.execute(query)

        medicines_with_reminders = result.scalars().unique().all()
        med_and_rem_final = []

        for medicine in medicines_with_reminders:
            med_and_rem_final.append(
                {
                    "id": medicine.id,
                    "name": medicine.name,
                    "dosage": medicine.dosage,
                    "reminder_time": medicine.reminders[0].reminder_time.strftime("%H:%M"),
                }
            )

        return med_and_rem_final

async def get_medicine_by_id(med_id: int) -> Medicine:
    async with async_session_maker() as session:
        query = select(Medicine).where(Medicine.id == med_id)
        result = await session.execute(query)
        medicine = result.scalar_one_or_none()
        return medicine

async def delete_medicine(medicine_id: int) -> None:
    async with async_session_maker() as session:
        medicine = await get_medicine_by_id(medicine_id)
        await session.delete(medicine)
        await session.commit()

async def is_less_than_10_reminders(tg_id: int) -> bool:
    user = await get_user_or_raise(tg_id=tg_id)

    async with async_session_maker() as session:
        query = select(Medicine).where(Medicine.user_id == user.id)
        result = await session.execute(query)
        medicines = result.scalars().all()

    if len(medicines) <= 10:
        return True

    return False
