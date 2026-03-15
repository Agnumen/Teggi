
import json
from pathlib import Path

CONFIG_FILE_PATH = Path("bot_config.json")

DEFAULT = {
        "ROUTINE_TEMPLATES": {
            "school_day": {
                "name": "🎒 Школьный день",
                "events": [
                    {"name": "Подъём и сборы", "start_time": "07:00", "end_time": "07:45", "tag": "quiet"},
                    {"name": "Дорога в школу", "start_time": "08:00", "end_time": "08:30", "tag": "active"},
                    {"name": "Уроки в школе", "start_time": "09:00", "end_time": "15:00", "tag": "loud"},
                    {"name": "Обед", "start_time": "12:00", "end_time": "12:30", "tag": "crowd"},
                    {"name": "Дорога домой", "start_time": "15:00", "end_time": "15:30", "tag": "dim"},
                    {"name": "Домашка", "start_time": "17:00", "end_time": "18:30", "tag": "bright"},
                    {"name": "Отдых / Хобби", "start_time": "19:00", "end_time": "20:00", "tag": "calm"},
                ]
            },
            "weekend_day": {
                "name": "🌳 День на каникулах",
                "events": [
                    {"name": "Свободное утро", "start_time": "10:00", "end_time": "12:00", "tag": "quiet"},
                    {"name": "Прогулка / Встреча", "start_time": "14:00", "end_time": "16:00", "tag": "crowd"},
                    {"name": "Хобби / Игры", "start_time": "17:00", "end_time": "19:00", "tag": "bright"},
                    {"name": "Ужин и отдых", "start_time": "19:30", "end_time": "21:00", "tag": "calm"},
                ]
            }
        },
        
        "TAGS": {
            "notag": ("⚖️ нейтрально", "Не забудь подготовиться!"),
            "quiet": ("🤫 тихо", "Обрати внимание на своё состояние. Тишина помогает сосредоточиться."),
            "loud": ("🔊 шумно", "Шум может мешать. Попробуй сделать паузу, чтобы перезагрузиться."),
            "crowd": ("👥 много людей", "Если становится тесно, найди момент для короткого перерыва."),
            "bright": ("💡 яркий свет","Свет влияет на настроение. Посмотри в окно, если глаза устают."),
            "dim": ("🌙 тусклый свет", "Вечерний свет приглушает ритм. Хорошее время для отдыха."),
            "calm": ("🧘‍♂️ спокойно", "Насладись моментом тишины и покоя. Он помогает восстановить баланс."),
        },
        "DAY_TAGS": {
            "🧘‍♂️ спокойно": "calm",
            "🏃‍♂️ активно": "active",
            "🤯 суетливо": "hectic",
            "😴 сонно": "sleepy"
        },
        "FEELINGS": {
            "🙂 Отлично": "great",
            "😐 Нормально": "ok",
            "🙁 Тяжело": "bad"
        },
    }

def _load_data():
    """Загружает данные из JSON файла."""
    if CONFIG_FILE_PATH.exists():
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    return DEFAULT

def save_data():
    """Сохраняет данные в JSON файл."""
    with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(BOT_CONFIG, f, ensure_ascii=False, indent=4)

BOT_CONFIG = _load_data()

ROUTINE_TEMPLATES = BOT_CONFIG["ROUTINE_TEMPLATES"]
TAGS = BOT_CONFIG["TAGS"]
DAY_TAGS = BOT_CONFIG["DAY_TAGS"]
FEELINGS = BOT_CONFIG["FEELINGS"]
