from aiogram.fsm.state import State, StatesGroup


class AddMedicine(StatesGroup):
    waiting_for_name = State()
    waiting_for_dosage = State()
    waiting_for_time = State()
    waiting_for_more_time = State()


class EditMedicine(StatesGroup):
    waiting_for_value = State()
