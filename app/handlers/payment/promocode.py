from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.buttons.inline_keyboard import back_keyboard
from app.service.promo_code import PromoCodeServiceController
from app.states import PromoCodeStates
from src.enums import ButtonCallback
from src.types import PromoCodeNameDTO

router = Router(name='promo_code')


@router.callback_query(F.data == ButtonCallback.PROMO_CODE)
async def promo_code(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="Введите промокод:",
        reply_markup=back_keyboard(callback_data=ButtonCallback.PAYMENTS)
    )
    await state.set_state(PromoCodeStates.code)


@router.message(PromoCodeStates.code)
async def input_promo_code(message: Message, state: FSMContext, session: AsyncSession):
    service = PromoCodeServiceController(session=session)

    try:
        promo_code_data = PromoCodeNameDTO(code=message.text or "")
        text = await service.activate(data=promo_code_data, telegram_id=message.from_user.id)

        await message.answer(
            text=text,
            reply_markup=back_keyboard(callback_data=ButtonCallback.PAYMENTS)
        )
        await state.clear()
    except ValidationError:
        await message.answer(
            text="Неверный формат промокода",
            reply_markup=back_keyboard(callback_data=ButtonCallback.PAYMENTS)
        )
        await state.clear()
