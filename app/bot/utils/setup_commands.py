from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from typing import Set

async def setup_bot_commands(bot: Bot, admin_ids: Set[int]):
    default_commands = [
        BotCommand(command="start", description="🚀 Открыть меню"),
        BotCommand(command="settings", description="⚙️ Настройки уведомлений"),
        BotCommand(command="demo", description="🧪 Запустить следующее событие"),
        BotCommand(command="demo_checkin", description=" 🧪 Запустить демонстрацию чекинов"),
    ]
    
    admin_commands = default_commands + [
        BotCommand(command="menu", description="⚙️ Админ панель"),
        BotCommand(command="stats", description="📊 Общая статистика бота"),
        BotCommand(command="active", description="🏆 Топ самых активных пользователей"),
        BotCommand(command="collected_data", description="🫂 Данные опроса"),
        BotCommand(command="methodology", description="🫂 Вопросы опроса"),
    ] 
    
    await bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())
    
    for admin_id in admin_ids:
        await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_id))