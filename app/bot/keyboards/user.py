from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.bot.templates import ROUTINE_TEMPLATES, TAGS, DAY_TAGS, FEELINGS

from app.infrastructure.database import Database

# main
def get_main_kb(has_routine: bool=True, key: str=None):
    builder = InlineKeyboardBuilder()
    key = 'school_day'
    template = ROUTINE_TEMPLATES.get(key)
    if has_routine:
        builder.button(text="🗓 Мой ритм на сегодня", callback_data="myrythm")
    else:
        builder.button(text=template["name"], callback_data=f"apply_template:{key}")
    builder.button(text="⚙️ Управление рутиной", callback_data="manage_routine")
    builder.adjust(1)
    return builder.as_markup()


cancel = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Отмена", callback_data="cancel_action")]]
)
manage = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="⚙️ Управление рутиной", callback_data="manage_routine")]]
)

# time
def get_time_picker_keyboard(prefix: str):
    builder = InlineKeyboardBuilder()
    for hour in range(7, 23):
        builder.button(text=str(hour), callback_data=f"{prefix}_hour:{hour:02d}")
    builder.adjust(4)
    builder.row(InlineKeyboardButton(text="Отмена", callback_data="cancel_action"))
    return builder.as_markup()

def get_minute_picker_keyboard(prefix: str):
    builder = InlineKeyboardBuilder()
    for minute in ["00", "15", "30", "45"]:
        builder.button(text=minute, callback_data=f"{prefix}_minute:{minute}")
    builder.adjust(4)
    builder.row(InlineKeyboardButton(text="⬅️ Назад к часам", callback_data=f"{prefix}_back_to_hours"))
    return builder.as_markup()

# tags
def get_sensory_tags_keyboard():
    builder = InlineKeyboardBuilder()
    for slug, data in TAGS.items():
        builder.button(text=data[0], callback_data=f"set_tag:{slug}")
    builder.adjust(2)
    return builder.as_markup()

def get_day_checkin_keyboard():
    builder = InlineKeyboardBuilder()
    for text, slug in DAY_TAGS.items():
        builder.button(text=text, callback_data=f"day_checkin:{slug}")
    builder.adjust(2)
    return builder.as_markup()

def get_evening_checkin_keyboard():
    builder = InlineKeyboardBuilder()
    for text, slug in FEELINGS.items():
        builder.button(text=text, callback_data=f"evening_checkin:{slug}")
    builder.adjust(3)
    return builder.as_markup()

# settings
async def get_settings_keyboard(user_id: int, db: Database):
    nott = await db.user.get_notifications_status_by_id(user_id)
    
    notifications_status = "✅ Включены" if nott else "❌ Выключены"
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Напоминания: {notifications_status}",
        callback_data="toggle_notifications",
    )
    return builder.as_markup()

def get_routine_management_keyboard(events: list):
    """Главный экран управления рутиной."""
    builder = InlineKeyboardBuilder()
    
    if events:
        builder.button(text="➕ Добавить еще событие", callback_data="add_event")
        
        for event in events:
             event_id = event.event_id
             builder.button(
                 text=f"🗑️ {event.start_time.strftime("%H:%M")} {event.name}",
                 callback_data=f"delete_event:{event_id}"
             )
    else:
        builder.button(text="➕ Создать первое событие", callback_data="add_event")
        builder.button(text="🔁 Повторить вчерашний план", callback_data="copy_yesterday")
        
    builder.button(text="➕ Добавить событие на другую дату", callback_data="add_event_for_date")
    builder.button(text="✨ Использовать шаблон", callback_data="use_template")
    if events:
        builder.button(text="❌ Очистить всю рутину", callback_data="clear_routine_confirm")
        
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ В главное меню", callback_data="back_to_main"))
    return builder.as_markup()

def get_routine_templates_keyboard():
    builder = InlineKeyboardBuilder()
    for key, template in ROUTINE_TEMPLATES.items():
        builder.button(text=template["name"], callback_data=f"apply_template:{key}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_manage"))
    return builder.as_markup()

def get_confirm_clear_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да, очистить", callback_data="clear_routine_confirmed")
    builder.button(text="Нет, отмена", callback_data="back_to_manage")
    return builder.as_markup()

