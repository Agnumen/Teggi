from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.infrastructure.database import Database
from app.bot.templates import TAGS
router = Router()

# Handlers for Check-ins
@router.callback_query(F.data.startswith("day_checkin:"))
async def process_day_checkin(callback: CallbackQuery, db: Database):
    _, slug = callback.data.split(":")
    await db.checkin.save_check_in(callback.from_user.id, "day", {"tag": slug})
    await callback.message.edit_text(f"Понял, сейчас обстановка — {TAGS.get(slug, ("notag", "No descr")[0])}. Спасибо, что поделился!")

@router.callback_query(F.data.startswith("evening_checkin:"))
async def process_evening_checkin(callback: CallbackQuery, db: Database):
    _, slug, feeling_text = callback.data.split(":")
    await db.checkin.save_check_in(callback.from_user.id, "evening", {"feeling": feeling_text})
    await callback.message.edit_text("Спасибо! Я учту это. Хорошего вечера!")
 