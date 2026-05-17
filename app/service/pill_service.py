from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.models import Medicine, Reminder
from app.db.session import async_session_maker
from app.service.reminder_service import parse_reminder_time, get_time_without_sec
from app.service.user_service import get_user_or_raise


async def create_medicine_and_reminder(
        tg_id: int,
        pill_name: str,
        dose: str,
        str_time: str
) -> tuple[Medicine, Reminder]:

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

        return medicine, reminder

async def create_medicine_and_reminders(
        tg_id: int,
        pill_name: str,
        dose: str,
        times: list[str]
) -> tuple[Medicine, list[Reminder]]:

    async with async_session_maker() as session:
        user = await get_user_or_raise(tg_id=tg_id)

        medicine = Medicine(
            user_id = user.id,
            name = pill_name,
            dosage = dose
        )
        session.add(medicine)
        await session.flush()

        reminders = []
        for str_time in times:
            parsed_time = parse_reminder_time(str_time)
            reminder = Reminder(
                medicine_id=medicine.id,
                reminder_time=parsed_time
            )
            session.add(reminder)
            reminders.append(reminder)

        await session.commit()
        await session.refresh(medicine)

        return medicine, reminders

async def get_medicines_and_reminders_list(tg_id: int) -> list:
    user = await get_user_or_raise(tg_id=tg_id)

    async with async_session_maker() as session:
        query = (
            select(Medicine)
            .options(joinedload(Medicine.reminders))
            .where(Medicine.user_id == user.id)
            .order_by(Medicine.id)
        )
        result = await session.execute(query)

        medicines_with_reminders = result.scalars().unique().all()
        med_and_rem_final = []

        for medicine in medicines_with_reminders:
            output_times = [get_time_without_sec(r.reminder_time) for r in medicine.reminders]
            med_and_rem_final.append(
                {
                    "id": medicine.id,
                    "name": medicine.name,
                    "dosage": medicine.dosage,
                    "reminder_time": output_times,
                }
            )

        if not med_and_rem_final:
            raise ValueError("Список таблеток пуст! Сперва добавьте хотя бы одну таблетку")

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

async def get_reminder_with_time(medicine_id: int) -> dict:
    async with async_session_maker() as session:
        query = (select(Medicine)
                 .options(joinedload(Medicine.reminders))
                 .where(Medicine.id == medicine_id))
        result = await session.execute(query)
        medicine = result.unique().scalar_one_or_none()
        output_times = []
        for rem in medicine.reminders:
            output_times.append(get_time_without_sec(rem.reminder_time))
        return {
            "name": medicine.name,
            "dosage": medicine.dosage,
            "times": output_times,
        }

async def edit_med_and_reminder(medicine_id: int, change_param: str, value: str) -> dict:
    async with async_session_maker() as session:
        query = (select(Medicine)
                 .options(joinedload(Medicine.reminders))
                 .where(Medicine.id == medicine_id))
        result = await session.execute(query)
        medicine = result.unique().scalar_one_or_none()

        if change_param == "name":
            medicine.name = value
        elif change_param == "dosage":
            medicine.dosage = value
        elif change_param == "time":
            reminder = medicine.reminders[0]
            reminder.reminder_time = parse_reminder_time(value)

        await session.commit()
        await session.refresh(medicine)

        return {"name": medicine.name, "dosage": medicine.dosage, "time": medicine.reminders[0].reminder_time}


async def is_less_than_10_reminders(tg_id: int) -> bool:
    user = await get_user_or_raise(tg_id=tg_id)

    async with async_session_maker() as session:
        query = select(Medicine).where(Medicine.user_id == user.id)
        result = await session.execute(query)
        medicines = result.scalars().all()

    if len(medicines) <= 10:
        return True

    return False
