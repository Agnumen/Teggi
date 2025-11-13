from aiogram import Router
from aiogram.types import Message, CallbackQuery

router = Router()

@router.message()
async def echo(msg: Message):
    await msg.answer("Извините, не пойму о чём речь 🤐")

@router.callback_query()
async def echo_call(call: CallbackQuery):
    await call.answer("Извините, не пойму о чём речь 🤐", show_alert=True)
