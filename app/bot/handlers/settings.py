from datetime import date
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from app.infrastructure.database import Database

from app.bot.keyboards import user as kb
from app.bot.scheduler.scheduler import setup_user_reminders, get_overview_for_user
from app.bot.templates import ROUTINE_TEMPLATES, TAGS

router = Router()

class EventCreation(StatesGroup):
    getting_date = State()
    getting_name = State()
    getting_start_hour = State()
    getting_start_minute = State()
    getting_end_hour = State()
    getting_end_minute = State()
    getting_tag = State()
    getting_tag_name = State()
    
# Routine center Main menu
async def show_routine_management_screen(message: Message | CallbackQuery, user_id: int, db: Database):
    events = await db.event.get_user_events(user_id)
    text = "⚙️ <b>Центр управления рутиной</b>\n\n"
    if not events:
        text += "Твой день пока пуст. Добавь событие или используй готовый шаблон, чтобы начать."
    else:
        text += "Вот твой текущий план на день:\n\n"
        for event in events:
            text += f"▪️ `{event.start_time.strftime("%H:%M")}-{event.end_time.strftime("%H:%M")}` — {event.name} ({TAGS.get(event.tag, ("notag", "Не забудь подготовитсья!"))[0]})\n"
    
    try:
        await message.message.edit_text(text, reply_markup=kb.get_routine_management_keyboard(events))
    except Exception as e:  # noqa: F841
        await message.answer(text, reply_markup=kb.get_routine_management_keyboard(events))

@router.callback_query(F.data.in_(["cancel_action","manage_routine"]))
async def manage_routine_entry(event: CallbackQuery, db: Database):
    await show_routine_management_screen(event, event.from_user.id, db)

# Templates Logic
@router.callback_query(F.data == "use_template")
async def choose_template(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выбери один из готовых шаблонов. Его можно будет изменить.",
        reply_markup=kb.get_routine_templates_keyboard()
    )

@router.callback_query(F.data.startswith("apply_template:"))
async def apply_template(callback: CallbackQuery, bot: Bot, scheduler: AsyncIOScheduler, db: Database):
    template_key = callback.data.split(":")[1]
    template = ROUTINE_TEMPLATES.get(template_key)
    user_id = callback.from_user.id

    if not template:
        await callback.answer("Шаблон не найден!", show_alert=True)
        return

    await callback.message.edit_text(f"Применяю шаблон «{template['name']}»...")
    
    await db.event.clear_user_routine(user_id)
    for event in template["events"]:
        await db.event.add_event(user_id, **event)
    
    await setup_user_reminders(user_id, bot, scheduler, db)
    await db.user.set_onboarding_complete(user_id)
    
    routine = await get_overview_for_user(callback.from_user.id, db)
    await callback.message.edit_text(routine, reply_markup=kb.manage)
    await callback.answer("Шаблон успешно применен!", show_alert=True)
    

# Handlers for event creation
@router.callback_query(F.data == "add_event")
async def start_event_creation(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EventCreation.getting_name)
    await state.update_data(event_date=date.today().isoformat())
    await callback.message.edit_text("Как назовем новое событие? (на сегодня)", reply_markup=kb.cancel)
    await callback.answer()
       
@router.callback_query(F.data == "add_event_for_date")
async def start_event_creation_for_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EventCreation.getting_date)
    await callback.message.edit_text(
        "Выберите дату для нового события:",
        reply_markup=await SimpleCalendar().start_calendar()
    )
    await callback.answer()

@router.callback_query(EventCreation.getting_date, SimpleCalendarCallback.filter())
async def process_date_selection(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected, event_date = await SimpleCalendar().process_selection(callback, callback_data)

    if selected:
        if event_date.date() < date.today():
            await callback.answer("Нельзя добавлять события в прошлом!", show_alert=True)
            return
        await state.update_data(event_date=event_date.date().isoformat())
        await state.set_state(EventCreation.getting_name)
        await callback.message.edit_text(
            f"Выбрана дата: {event_date.date().strftime('%d.%m.%Y')}. Как назовем событие?",
            reply_markup=kb.cancel
        )
        
@router.message(EventCreation.getting_name)
async def process_event_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(EventCreation.getting_start_hour)
    await message.answer("Отлично! Теперь выбери <b>час начала</b> события:", reply_markup=kb.get_time_picker_keyboard("start"))


# Chain of handlers for time picking
@router.callback_query(EventCreation.getting_start_hour, F.data.startswith("start_hour:"))
async def process_start_hour(callback: CallbackQuery, state: FSMContext):
    hour = callback.data.split(":")[1]
    await state.update_data(start_hour=hour)
    await state.set_state(EventCreation.getting_start_minute)
    await callback.message.edit_text(f"Час начала: {hour}. Теперь выбери <b>минуты</b>:", reply_markup=kb.get_minute_picker_keyboard("start"))

@router.callback_query(EventCreation.getting_start_minute, F.data.endswith("_back_to_hours"))
async def process_back_to_start_hour(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EventCreation.getting_start_hour)
    await callback.message.edit_text("Отлично! Теперь выбери <b>час начала</b> события:", reply_markup=kb.get_time_picker_keyboard("start"))
    
@router.callback_query(EventCreation.getting_start_minute, F.data.startswith("start_minute:"))
async def process_start_minute(callback: CallbackQuery, state: FSMContext):
    minute = callback.data.split(":")[1]
    await state.update_data(start_minute=minute)
    await state.set_state(EventCreation.getting_end_hour)
    data = await state.get_data()
    await callback.message.edit_text(f"Время начала: {data['start_hour']}:{minute}. Теперь выбери <b>час окончания</b>:", reply_markup=kb.get_time_picker_keyboard("end"))

@router.callback_query(EventCreation.getting_end_hour, F.data.startswith("end_hour:"))
async def process_end_hour(callback: CallbackQuery, state: FSMContext):
    hour = callback.data.split(":")[1]
    data = await state.get_data()
    if int(data["start_hour"]) > int(hour):
        await callback.answer("Время завершения должно быть посла старта. Или наоборот?", show_alert=True)
        return
    await state.update_data(end_hour=hour)
    await state.set_state(EventCreation.getting_end_minute)
    await callback.message.edit_text(f"Час окончания: {hour}. Теперь выбери <b>минуты</b>:", reply_markup=kb.get_minute_picker_keyboard("end"))

@router.callback_query(EventCreation.getting_end_minute, F.data.endswith("_back_to_hours"))
async def process_back_to_end_hour(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EventCreation.getting_end_hour)
    data = await state.get_data()
    await callback.message.edit_text(f"Время начала: {data['start_hour']}:{data['start_minute']}. Теперь выбери <b>час окончания</b>:", reply_markup=kb.get_time_picker_keyboard("end"))

@router.callback_query(EventCreation.getting_end_minute, F.data.startswith("end_minute:"))
async def process_end_minute(callback: CallbackQuery, state: FSMContext):
    minute = callback.data.split(":")[1]
    data = await state.get_data()
    if int(data["start_hour"]) == int(data["end_hour"]) and int(data["start_minute"]) >= int(minute):
        await callback.answer("Время завершения должно быть посла старта. Или наоборот?", show_alert=True)
        return
    await state.update_data(end_minute=minute)
    await state.set_state(EventCreation.getting_tag)
    await callback.message.edit_text(
        f"Время: {data['start_hour']}:{data['start_minute']} - {data['end_hour']}:{minute}.\n\n"
        f"Какая там обычно обстановка?", reply_markup=kb.get_sensory_tags_keyboard()
    )

# Final step
@router.callback_query(EventCreation.getting_tag, F.data.startswith("set_tag:"))
async def process_tag_and_finish(callback: CallbackQuery, state: FSMContext, bot: Bot, scheduler: AsyncIOScheduler, db: Database):
    _, slug = callback.data.split(":")
    
    data = await state.get_data()
    event_date = date.fromisoformat(data["event_date"])
    start_time = f"{data['start_hour']}:{data['start_minute']}"
    end_time = f"{data['end_hour']}:{data['end_minute']}"

    await db.event.add_event(
        user_id=callback.from_user.id, name=data['name'],
        start_time=start_time, end_time=end_time, tag=slug, event_date=event_date
    )
    
    await state.clear()
    await setup_user_reminders(callback.from_user.id, bot, scheduler, db, event_date)
    await db.user.set_onboarding_complete(callback.from_user.id)
    
    overview = await get_overview_for_user(callback.from_user.id, db, event_date)
    if overview:
        await callback.message.edit_text(overview, reply_markup=kb.manage)
    else:
        await show_routine_management_screen(callback, callback.from_user.id, db)
    
    await callback.answer(f"Событие '{data['name']}' добавлено на {event_date.strftime('%d.%m.%Y')}!")
   

# Clear and back Logic
@router.callback_query(F.data.startswith("delete_event:"))
async def process_delete_event(callback: CallbackQuery, bot: Bot, db: Database, scheduler: AsyncIOScheduler):
    event_id = callback.data.split(":")[1]
    user_id = callback.from_user.id

    deleted = await db.event.delete_event(event_id)
    if deleted:
        await callback.answer("Событие удалено", show_alert=True)
        await setup_user_reminders(user_id, bot, scheduler, db)
        await show_routine_management_screen(callback, user_id, db)
    else:
        await callback.answer("Не удалось удалить событие.", show_alert=True)
        
@router.callback_query(F.data == "clear_routine_confirm")
async def confirm_clear_routine(callback: CallbackQuery):
    await callback.message.edit_text(
        "Ты уверен, что хочешь удалить все события из рутины?",
        reply_markup=kb.get_confirm_clear_keyboard()
    )

@router.callback_query(F.data == "clear_routine_confirmed")
async def process_clear_routine(callback: CallbackQuery, bot: Bot, scheduler: AsyncIOScheduler, db: Database):
    user_id = callback.from_user.id
    await db.event.clear_user_routine(user_id)
    await setup_user_reminders(user_id, bot, scheduler, db)
    await show_routine_management_screen(callback, user_id, db)
    await callback.answer("Рутина очищена.", show_alert=True)

@router.callback_query(F.data == "back_to_manage")
async def back_to_management(callback: CallbackQuery, db: Database):
    await show_routine_management_screen(callback, callback.from_user.id, db)
    await callback.answer()


