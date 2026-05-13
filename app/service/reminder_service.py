from datetime import time, datetime


def parse_reminder_time(time_to_remind: str) -> time:
    try:
        return datetime.strptime(time_to_remind, "%HH:%MM").time()
    except ValueError:
        raise ValueError("Время должно быть указано в формате ЧЧ:ММ, например 09:30")
