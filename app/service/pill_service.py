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
