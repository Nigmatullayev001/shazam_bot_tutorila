
from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    name = State()
    age = State()
    address = State()
    photo = State()


