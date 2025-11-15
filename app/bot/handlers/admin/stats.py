# from os import getenv
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

    text = f"""📊 **Статистика бота "НейроРитм"**

- **Всего пользователей:** {stats['total_users']}
- **Прошли онбординг:** {stats['onboarding_completion_rate']:.2f}%
- **Retention (активные за 7 дней):** {stats['retention_7_days_count']}
- **Всего чек-инов:** {stats['total_checkins']}
- **Среднее кол-во чек-инов в день:** {stats['avg_checkins_per_day']:.2f}
"""
    await message.answer(text, parse_mode="Markdown")

@router.message(Command("active"))
async def cmd_active(message: Message, db: Database):
    stats = await db.activity.get_statistics()
    
    await message.answer("📊 <b>Топ активных пользователей</b>\n"+"\n".join(
                f"{i}. <b>{stat[0]}</b>: {stat[1]}"
                for i, stat in enumerate(stats, 1)
            ))
    