from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Шаблоны рутин", callback_data="edit_routines")],
        [InlineKeyboardButton(text="Советы (TIPS)", callback_data="edit_simple_dict:TIPS")],
        [InlineKeyboardButton(text="Теги (tags)", callback_data="edit_simple_dict:TAGS")],
        [InlineKeyboardButton(text="Теги дня (day_tags)", callback_data="edit_simple_dict:DAY_TAGS")],
        [InlineKeyboardButton(text="Ощущения (feelings)", callback_data="edit_simple_dict:FEELINGS")],
        [InlineKeyboardButton(text="❌ Закрыть", callback_data="close_admin_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_edit_kb(data):
    builder = InlineKeyboardBuilder()
    
    if data:
        for key in data:
            builder.button(text=f"✏️ {key}", callback_data=f"edit_item:{key}")
    
    builder.button(text="➕ Добавить новый", callback_data="add_new_item")
    builder.button(text="⬅️ Назад", callback_data="back_to_main_menu")
    
    builder.adjust(1)
    return builder.as_markup()

def get_key_edit_kb(dict_key):
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📝 Изменить значение", callback_data="change_value")
    builder.button(text="🗑️ Удалить запись", callback_data="delete_item")
    builder.button(text="⬅️ Назад к списку", callback_data=f"edit_simple_dict:{dict_key}")
    
    builder.adjust(1)
    return builder.as_markup()