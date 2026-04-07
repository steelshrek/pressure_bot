from aiogram.fsm.state import StatesGroup, State


class MeasuresSetup(StatesGroup):
    sending_photo = State()
    confirming_data = State()
    sending_manual = State()


class OptionSetup(StatesGroup):
    changingMorning = State()
    changingEvening = State()
