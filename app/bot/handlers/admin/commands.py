from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

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

@router.message(Command("collected_data"))
async def show_collected_data(message: Message):
    stats_text =(
        """Пилотное исследование (декабрь 2025)
        
        Участники: 30 подростков, 15 17 лет, школа №29 «армония
        Данные анонимны, персональная информация не сохраняется
        Ключевые метрики:
        83.3% — тревожность из-за учебной нагрузки
        76.7% — хроническая усталость
        93.3% — скрывают эмоциональное состояние от родителей
        
        Метрики использования:
        86.7% — прошли онбординг менее 2 мин
        70% — повторное использование в течение недели
        4.3/5 — средняя удовлетворённость (шкала Лайкерта)
        
        Эти данные используются как референс для персонализации рекомендаций."""
    )
    await message.answer(stats_text)

@router.message(Command("methodology"))
async def show_methodology(message: Message):
    methodology = (
        """Методика сбора данных
        Опрос проводился в декабре 2025 г. среди учеников 15–17 лет школы №29 «Гармония».
        Формат: анонимная анкета + интервью. Участие добровольное.
        Вопросы анкеты:
                
        Блок 1: Психоэмоциональное состояние
        1. Как часто ты чувствуешь усталость, даже если хорошо выспался?
           Почти каждый день / 2–3 раза в неделю / Реже раза в неделю
        
        2. Испытываешь ли ты тревогу или напряжение перед уроками, контрольными, ответами у доски?
           Да, почти всегда / Иногда / Редко или никогда
        
        3. Делишься ли ты с родителями, когда у тебя плохое настроение или стресс?
           Нет, предпочитаю скрывать / Иногда, если спросят / Да, всегда рассказываю
        
        Блок 2: Сенсорная среда и потребности
        4. Что чаще всего мешает тебе сосредоточиться?
           Шум / Яркий свет / Много людей вокруг / Телефон / Другое
        
        5. Хотел(а) бы ты получать короткие персональные советы по тому, как легче справляться с нагрузкой в течение дня?
           Да, это было бы полезно / Возможно / Нет, не нужно
        
        В текущей версии MVP эти вопросы зафиксированы как референс. В релизной версии сбор ответов будет автоматизирован через команду /feedback внутри бота с сохранением в анонимизированной БД.
        
        Блок 3: Обратная связь по прототипу
        1. Оцени удобство использования бота по шкале от 1 до 5
           1 / 2 / 3 / 4 / 5
        
        Что запомнилось или понравилось больше всего?"""
    )
    await message.answer(methodology)