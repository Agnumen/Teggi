import logging
from datetime import datetime as dt, timedelta, date
from zoneinfo import ZoneInfo

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.bot.keyboards.user import get_evening_checkin_keyboard, get_day_checkin_keyboard
from app.core.AI import Advisor_AI
from app.bot.templates import TAGS

from app.infrastructure.database import Database
logger = logging.getLogger(__name__)

async def send_many_messages(bot: Bot, text: str, db: Database):
    user_ids = await db.user.get_all_user_ids()

    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text)
        except Exception as e:  # noqa: F841
            pass

    
async def send_morning_overview(bot: Bot, db: Database):
    user_ids = await db.user.get_all_user_ids()
    event_date = dt.now(ZoneInfo("Europe/Moscow")).date()
    for user_id in user_ids:
        text = await get_overview_for_user(user_id, db, event_date=event_date)
        if text:
            await bot.send_message(user_id, text)

async def send_day_checkin(bot: Bot, db: Database):
    user_ids = await db.user.get_all_user_ids()
    for user_id in user_ids:
        await bot.send_message(user_id, "Как ты сейчас? Какая обстановка вокруг?", reply_markup=get_day_checkin_keyboard())


async def send_evening_checkin(bot: Bot, db: Database):
    user_ids = await db.user.get_all_user_ids()
    for user_id in user_ids:
        await bot.send_message(user_id, "Как прошёл день в целом?", reply_markup=get_evening_checkin_keyboard())

async def send_reminder(bot: Bot, user_id: int, event_name: str, tag: str, db: Database, advisor: Advisor_AI):
    await db.user.get_or_create_user(user_id)
    
    if not await db.user.get_notifications_status_by_id(user_id):
        return
    info, used_ai = await advisor.get_advice(event_name, tag)
    tip = '✨ ' if used_ai else '📚 ' 
    tip += info[0]
    tag = info[1]
    await bot.send_message(user_id, f"🔔 Через 15 минут — <b>{event_name}</b> ({tag})\n\n<i>{tip}</i>")

async def setup_user_reminders(user_id: int, bot: Bot, scheduler: AsyncIOScheduler, db: Database, advisor: Advisor_AI, event_date: date = None):
    if event_date is None:
        event_date = dt.now(ZoneInfo("Europe/Moscow")).date()
    for job in scheduler.get_jobs():
        if job.id.startswith(f"reminder_{user_id}_{event_date.strftime('%Y%m%d')}_"):
            job.remove()

    events = await db.event.get_user_events(user_id, event_date=event_date)
    now_msk = dt.now(ZoneInfo("Europe/Moscow"))
    
    for event in events:
        try:
            reminder_time = dt.combine(event_date, event.start_time,  tzinfo=ZoneInfo("Europe/Moscow")) - timedelta(minutes=15)
            
            if reminder_time < now_msk:
                continue
            
            job_id = f"reminder_{user_id}_{event_date.strftime('%Y%m%d')}_{event.id}"
            scheduler.add_job(
                send_reminder,
                trigger="date",
                run_date=reminder_time,
                kwargs={"bot": bot, "user_id": user_id, "event_name": event.name, "tag": event.tag, "db": db, "advisor": advisor},
                id=job_id,
                replace_existing=True
            )
            logger.debug(f"SCHEDULER: Added reminder for {user_id} at {reminder_time.strftime('%H:%M')} for event '{event.name}'")
        except Exception as e:
            logger.error(f"Error scheduling reminder for {user_id} on event {event.name}: {e}")


async def get_overview_for_user(user_id: int, db: Database, event_date: date = None) -> bool | str:
    if event_date is None:
        event_date = dt.now(ZoneInfo("Europe/Moscow")).date()
    events = await db.event.get_user_events(user_id, event_date)
    if not events:
        return None
    moscow_now = dt.now(ZoneInfo("Europe/Moscow")).date()
    date_str = "сегодня" if event_date == moscow_now else event_date.strftime("%d.%m.%Y")
    overview_text = f"Вот твой ритм на {date_str} 👇\n\n"
    for event in events:
        overview_text += f"<b>{event.start_time.strftime('%H:%M')}–{event.end_time.strftime('%H:%M')}</b> — {event.name} ({TAGS.get(event.tag, ("notag", "Не забудь подготовиться!"))[0]})\n"
    overview_text += "\n\nХорошего дня!"
    try:
        return overview_text
    except Exception as e:
        logger.error(f"Failed to send overview to {user_id}: {e}")
        return False

def setup_scheduler(bot: Bot, session_pool: async_sessionmaker[AsyncSession]):
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Europe/Moscow"))
    
    async def scheduled_morning_overview():
        async with session_pool() as session:
            db = Database(session=session)
            await send_morning_overview(bot, db)
    
    async def scheduled_day_checkin():
        async with session_pool() as session:
            db = Database(session=session)
            await send_day_checkin(bot, db)
    
    async def scheduled_evening_checkin():
        async with session_pool() as session:
            db = Database(session=session)
            await send_evening_checkin(bot, db)
    
    scheduler.add_job(scheduled_morning_overview, "cron", hour=7, minute=30, timezone=ZoneInfo("Europe/Moscow"), misfire_grace_time=None)
    scheduler.add_job(scheduled_day_checkin, "cron", hour=13, minute=0, timezone=ZoneInfo("Europe/Moscow"), misfire_grace_time=None)
    scheduler.add_job(scheduled_evening_checkin, "cron", hour=20, minute=30, timezone=ZoneInfo("Europe/Moscow"), misfire_grace_time=None)
    
    return scheduler
