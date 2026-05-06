from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.keyboards import user as kb
from app.bot.scheduler.scheduler import get_overview_for_user, send_reminder
from app.bot.keyboards.user import get_day_checkin_keyboard, get_evening_checkin_keyboard
from app.core.AI import Advisor_AI

from app.infrastructure.database import Database

router = Router()

# basic commands
@router.message(CommandStart())
async def cmd_start(message: Message, db: Database, state: FSMContext):
    if state is not None:
        await state.clear()
    user = await db.user.get_or_create_user(message.from_user.id)
    
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
async def cmd_settings(message: Message, db: Database, state: FSMContext):
    if state is not None:
        await state.clear()
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

@router.message(Command("demo"))
async def force_next_event(message: Message, bot: Bot, db: Database, advisor: Advisor_AI):
    user_id = message.from_user.id
    next_event = await db.event.get_next_event_by_user_id(user_id)
    
    if next_event is None:
        await message.answer(
            "⚠️ У Вас нет запланированных событий.\n"
            "Сначала добавьте событие."
        )
        return
    try:
        await send_reminder(bot, user_id, next_event.name, next_event.tag, db, advisor)

        await message.answer("✅ Демо-событие отправлено")
    except Exception as e:
        await message.answer(f"Ошибка отправки!")
        
@router.message(Command("demo_checkin"))
async def cmd_demo(message: Message):
    await message.answer("🚀 Запускаю демонстрацию всех рассылок...")
    
    await message.answer("Как ты сейчас? Какая обстановка вокруг?", reply_markup=get_day_checkin_keyboard())
    
    await message.answer("Как прошёл день в целом?", reply_markup=get_evening_checkin_keyboard())
    