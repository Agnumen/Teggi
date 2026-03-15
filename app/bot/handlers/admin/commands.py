from datetime import datetime as dt
from zoneinfo import ZoneInfo
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.bot.scheduler.scheduler import send_reminder, get_overview_for_user
from app.bot.keyboards.user import get_day_checkin_keyboard, get_evening_checkin_keyboard

from app.core.AI import Advisor_AI

from app.infrastructure.database import Database

router = Router()

@router.message(Command("stats"))
async def cmd_stats(message: Message, db: Database):

    stats = await db.user.get_statistics()
    if "error" in stats:
        return await message.answer(stats["error"])

    text = f"""<b>Статистика бота "Тегги"</b>

- <b>Всего пользователей:</b> {stats['total_users']}
- <b>Прошли онбординг:</b> {stats['onboarding_completion_rate']:.2f}%
- <b>Retention (активные за 7 дней):</b> {stats['retention_7_days_count']}
- <b>Всего чек-инов:</b> {stats['total_checkins']}
- <b>Среднее кол-во чек-инов в день:</b> {stats['avg_checkins_per_day']:.2f}
"""
    await message.answer(text)

@router.message(Command("active"))
async def cmd_active(message: Message, db: Database):
    stats = await db.activity.get_statistics()
    
    await message.answer("<b>Топ активных пользователей</b>\n"+"\n".join(
                f"{i}. <b>{stat[0]}</b>: {stat[1]}"
                for i, stat in enumerate(stats, 1)
            ))
    
@router.message(Command("demo"))
async def cmd_demo(message: Message, bot: Bot, db: Database):
    await message.answer("🚀 Запускаю демонстрацию всех рассылок...")
    
    event_date = dt.now(ZoneInfo("Europe/Moscow")).date()
    user_id = message.from_user.id
    text = await get_overview_for_user(user_id, db, event_date=event_date)
    if text:
        await message.answer(text)
        
    await bot.send_message(user_id, "Как ты сейчас? Какая обстановка вокруг?", reply_markup=get_day_checkin_keyboard())
    
    await bot.send_message(user_id, "Как прошёл день в целом?", reply_markup=get_evening_checkin_keyboard())
    
@router.message(Command("demo_event"))
async def force_next_event(message: Message, bot: Bot, db: Database, advisor: Advisor_AI):
    user_id = message.from_user.id
    next_event = await db.event.get_next_event_by_user_id(user_id)
    
    if next_event is None:
        await message.answer(
            f"⚠️ У пользователя {user_id} нет запланированных событий.\n"
            "Сначала добавьте событие."
        )
        return
    try:
        await send_reminder(bot, user_id, next_event.name, next_event.tag, db, advisor)

        await message.answer("✅ Демо-событие отправлено")
    except Exception as e:
        await message.answer(f"Ошибка отправки {str(e)}")
