from aiogram.dispatcher.filters.state import State, StatesGroup


class Insta(StatesGroup):
    load = State()
    send = State()


class YouTube(StatesGroup):
    load = State()
    send = State()
