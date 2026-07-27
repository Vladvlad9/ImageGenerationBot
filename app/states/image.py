from aiogram.fsm.state import StatesGroup, State

__all__ = ['ImageStates']


class ImageStates(StatesGroup):
    prompt = State()
    style_photo = State()
