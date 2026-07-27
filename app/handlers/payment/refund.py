from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

router = Router(name="refund")


@router.message(Command("refund"))
async def refund(message: Message, bot: Bot, command: CommandObject):
    t_id = command.args

    if t_id is None:
        await message.answer(text="donate-refund-input-error")
        return

    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=t_id
        )
        await message.answer(text="refund success")
    except TelegramBadRequest as e:
        err_msg = "refund-code-not-found"

        if "CHARGE_ALREADY_REFUNDED" in e.message:
            err_msg = "refund-already-refunded"

        await message.answer(text=err_msg)
    return
