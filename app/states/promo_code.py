from aiogram.fsm.state import StatesGroup, State

__all__ = ['PromoCodeStates']


class PromoCodeStates(StatesGroup):
    code = State()
