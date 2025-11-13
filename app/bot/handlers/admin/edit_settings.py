from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter

from app.bot.keyboards import admin
from app.bot.templates import save_data, BOT_CONFIG

# FSM States
class AdminConfig(StatesGroup):
    main_menu = State()
    
    # Состояния для простых словарей (TIPS, TAGS, etc.)
    simple_dict_list = State()
    adding_simple_key = State()
    adding_simple_value = State()
    editing_simple_value = State()
    
    # Состояния для шаблонов рутин
    routine_list = State()
    routine_details = State()
    editing_routine_name = State()
    event_list = State()
    adding_event = State()
    editing_event = State()

router = Router()

# --- Хендлеры ---

@router.message(Command("templates"))
async def cmd_admin_config(message: Message, state: FSMContext):
    """Входная точка для редактирования конфигурации."""
    await state.set_state(AdminConfig.main_menu)
    await message.answer(
        "Добро пожаловать в меню администратора.\n\n"
        "⚠️ **Внимание:** Все изменения сохраняются в файл `bot_config.json`.",
        reply_markup=admin.get_main_menu_keyboard()
    )

@router.callback_query(F.data == "close_admin_menu")
async def close_menu(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()

# --- Логика для простых словарей (TIPS, TAGS и т.д.) ---

@router.callback_query(F.data.startswith("edit_simple_dict:"))
async def list_simple_dict_items(callback: CallbackQuery, state: FSMContext):
    dict_key = callback.data.split(":")[1]
    data = BOT_CONFIG[dict_key]
    
    await state.update_data(current_dict_key=dict_key)
    await state.set_state(AdminConfig.simple_dict_list)

    text = f"Редактирование **{dict_key}**:\n\n"
    
    await callback.message.edit_text(text, reply_markup=admin.get_edit_kb(data))

@router.callback_query(StateFilter(AdminConfig.simple_dict_list), F.data == "add_new_item")
async def add_simple_item_key(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminConfig.adding_simple_key)
    await callback.message.edit_text("Отправьте мне новый **ключ** (например, `🙂 Отлично` или `🧘‍♂️ спокойно`).")

@router.message(StateFilter(AdminConfig.adding_simple_key))
async def process_simple_item_key(message: Message, state: FSMContext):
    await state.update_data(new_key=message.text)
    await state.set_state(AdminConfig.adding_simple_value)
    await message.answer("Отлично. Теперь отправьте мне **значение** для этого ключа (например, `great` или `calm`).")

@router.message(StateFilter(AdminConfig.adding_simple_value))
async def process_simple_item_value(message: Message, state: FSMContext):
    data = await state.get_data()
    dict_key = data['current_dict_key']
    new_key = data['new_key']
    new_value = message.text

    BOT_CONFIG[dict_key][new_key] = new_value
    save_data() # Сохраняем изменения

    await message.answer(f"✅ Запись `{new_key}: {new_value}` добавлена в **{dict_key}**.")
    
    # Возвращаемся к списку
    # Это эмуляция вызова хендлера, чтобы показать обновленное меню
    callback_mock = type('obj', (object,), {'data': f'edit_simple_dict:{dict_key}', 'message': message})
    await list_simple_dict_items(callback_mock, state)

@router.callback_query(StateFilter(AdminConfig.simple_dict_list), F.data.startswith("edit_item:"))
async def edit_simple_item(callback: CallbackQuery, state: FSMContext):
    item_key = callback.data.split(":", 1)[1]
    data = await state.get_data()
    dict_key = data['current_dict_key']
    current_value = BOT_CONFIG[dict_key].get(item_key)

    await state.update_data(editing_key=item_key)
    
    
    text = f"Выбран ключ: `{item_key}`\nТекущее значение: `{current_value}`\n\nЧто вы хотите сделать?"
    await callback.message.edit_text(text, reply_markup=admin.get_key_edit_kb(dict_key))

@router.callback_query(StateFilter(AdminConfig.simple_dict_list), F.data == "change_value")
async def change_simple_item_value(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminConfig.editing_simple_value)
    await callback.message.answer("Отправьте новое значение для этого ключа.")

@router.message(StateFilter(AdminConfig.editing_simple_value))
async def process_new_simple_item_value(message: Message, state: FSMContext):
    data = await state.get_data()
    dict_key = data['current_dict_key']
    item_key = data['editing_key']
    
    BOT_CONFIG[dict_key][item_key] = message.text
    save_data()

    await message.answer(f"✅ Значение для ключа `{item_key}` обновлено.")
    
    callback_mock = type('obj', (object,), {'data': f'edit_simple_dict:{dict_key}', 'message': message})
    await list_simple_dict_items(callback_mock, state)


@router.callback_query(StateFilter(AdminConfig.simple_dict_list), F.data == "delete_item")
async def delete_simple_item(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    dict_key = data['current_dict_key']
    item_key = data['editing_key']
    
    if item_key in BOT_CONFIG[dict_key]:
        del BOT_CONFIG[dict_key][item_key]
        save_data()
        await callback.answer(f"✅ Запись `{item_key}` удалена.", show_alert=True)
    else:
        await callback.answer("❗️ Запись уже удалена.", show_alert=True)
        
    callback_mock = type('obj', (object,), {'data': f'edit_simple_dict:{dict_key}', 'message': callback.message})
    await list_simple_dict_items(callback_mock, state)


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню."""
    await state.set_state(AdminConfig.main_menu)
    await callback.message.edit_text(
        "Главное меню администратора.",
        reply_markup=admin.get_main_menu_keyboard()
    )