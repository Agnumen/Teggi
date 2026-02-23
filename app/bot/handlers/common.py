from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from app.bot.keyboards import user as kb
from app.infrastructure.database import Database

from app.bot.scheduler.scheduler import get_overview_for_user

router = Router()

# basic commands
@router.message(CommandStart())
async def cmd_start(message: Message, db: Database):
    await db.user.get_or_create_user(message.from_user.id)
    sent = await get_overview_for_user(message.from_user.id, db)
    if sent is None:
        keyboard = kb.get_main_kb(False)
    else:
        keyboard = kb.get_main_kb()
    await message.answer(
        "Привет! Я — Тегги. Помогу тебе построить день спокойнее, учитывая обстановку вокруг.\n\nДля начала работы можешь воспользоваться готовым шаблоном (рекомендуется).",
        reply_markup=keyboard
    )

@router.message(Command("settings"))
async def cmd_settings(message: Message, db: Database):
    await db.user.get_or_create_user(message.from_user.id)
    keyb = await kb.get_settings_keyboard(message.from_user.id, db)
    await message.answer("Настройки уведомлений:", reply_markup=keyb)
    
@router.callback_query(F.data == "toggle_notifications")
async def toggle_notifications(callback: CallbackQuery, db: Database):
    new_status = await db.user.toggle_notifications(callback.from_user.id)
    
    keyb = await kb.get_settings_keyboard(callback.from_user.id, db)
    await callback.message.edit_reply_markup(reply_markup=keyb)
    await callback.answer(f"Напоминания {'включены' if new_status else 'выключены'}", show_alert=True)

@router.callback_query(F.data=="myrythm")
@router.callback_query(F.data == "back_to_main")
async def show_today_routine(callback: CallbackQuery, db: Database):
    await db.user.get_or_create_user(callback.from_user.id)
    sent = await get_overview_for_user(callback.from_user.id, db)
    if sent is None:
        await callback.message.edit_text("Твоя рутина пуста.\nНастрой её в меню '⚙️ Управление рутиной'.", reply_markup=kb.get_main_kb(False))
        return
    await callback.message.edit_text(sent, reply_markup=kb.manage)
