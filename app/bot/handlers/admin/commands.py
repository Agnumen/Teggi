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

@router.message(Command("collected_data"))
async def show_collected_data(message: Message):
    stats_text =(
        """📊 <b>Пилотное исследование (декабрь 2025)</b>
        
        👥 Участники: 30 подростков, 15–17 лет, школа №29 «Гармония»
        🔒 Данные анонимны, персональная информация не сохраняется
        <b>Ключевые метрики:</b>
        • 83.3% — тревожность из-за учебной нагрузки
        • 76.7% — хроническая усталость
        • 93.3% — скрывают эмоциональное состояние от родителей
        
        <b>Метрики использования:</b>
        • 86.7% — прошли онбординг < 2 мин
        • 70% — повторное использование в течение недели
        • 4.3/5 — средняя удовлетворённость (шкала Лайкерта)
        
        <i>Эти данные используются как референс для персонализации рекомендаций.</i>"""
    )
    await message.answer(stats_text)

@router.message(Command("methodology"))
async def show_methodology(message: Message):
    methodology = (
        """📋 <b>Методика сбора данных (Пилот)</b>
        Опрос проводился в декабре 2025 г. среди учеников 15–17 лет школы №29 «Гармония».
        Формат: анонимная анкета + интервью. Участие добровольное.
        <b>📝 Вопросы анкеты (оригинал):</b>
        
        <b>Блок 1: Психоэмоциональное состояние</b>
        1. <i>Как часто ты чувствуешь усталость, даже если хорошо выспался?</i>
           • Почти каждый день / • 2–3 раза в неделю / • Реже раза в неделю
        
        2. <i>Испытываешь ли ты тревогу или напряжение перед уроками, контрольными, ответами у доски?</i>
           • Да, почти всегда / • Иногда / • Редко или никогда
        
        3. <i>Делишься ли ты с родителями, когда у тебя плохое настроение или стресс?</i>
           • Нет, предпочитаю скрывать / • Иногда, если спросят / • Да, всегда рассказываю
        
        <b>Блок 2: Сенсорная среда и потребности</b>
        4. <i>Что чаще всего мешает тебе сосредоточиться?</i> (можно выбрать несколько)
           • Шум / • Яркий свет / • Много людей вокруг / • Телефон / • Другое
        
        5. <i>Хотел(а) бы ты получать короткие персональные советы по тому, как легче справляться с нагрузкой в течение дня?</i>
           • Да, это было бы полезно / • Возможно / • Нет, не нужно
        
        <i>⚠️ В текущей версии MVP эти вопросы зафиксированы как референс. В релизной версии сбор ответов будет автоматизирован через команду /feedback внутри бота с сохранением в анонимизированной БД.</i>"""
    )
    await message.answer(methodology)