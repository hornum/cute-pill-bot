from datetime import time, datetime


def parse_reminder_time(time_to_remind: str) -> time:
    try:
        return datetime.strptime(time_to_remind, "%H:%M").time()
    except ValueError:
        raise ValueError(f"Время должно быть указано в формате ЧЧ:ММ, например 09:30")

def get_time_without_sec(time_to_remind: time) -> str:
    return time_to_remind.strftime("%H:%M")
