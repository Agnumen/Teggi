import logging
from asyncio import TimeoutError, wait_for
from typing import Tuple
from yandex_gpt import YandexGPT, YandexGPTConfigManagerForAPIKey
from config import Settings

from app.bot.templates import TAGS

logger = logging.getLogger(__name__)
class Advisor_AI:
    def __init__(self, catalog_id: str, api_key: str):
        self.catalog_id = catalog_id
        self.api_key = api_key
        self._client = None
        try:
            self._client = YandexGPT(
                config_manager=YandexGPTConfigManagerForAPIKey(
                model_type="yandexgpt-lite",
                catalog_id=self.catalog_id,
                api_key=self.api_key,
                )
            )
            logger.info("YandexGPT successfully connected!")
        except Exception as e:
            logger.error(f"Error connecting YandexGPT: {e}")
            
    def _get_prompt(self, activity: str, tag: str) -> str:
        return f"""
Ты — помощник по саморегуляции для подростков. Твоя задача — дать короткий, практичный совет, который поможет справиться с сенсорной нагрузкой.

КОНТЕКСТ:
- Активность: "{activity}"
- Сенсорный тег: {tag}

ПРАВИЛА:
1. Совет должен быть коротким (1-2 предложения)
2. Используй дружелюбный, поддерживающий тон
3. Не давай общих фраз — совет должен быть конкретным
4. Избегай морализаторства ("ты должен", "обязательно")
5. Используй конструкции: "Можно попробовать...", "Помогает...", "Обрати внимание..."

ФОРМАТ ОТВЕТА:
Только совет, без лишних слов.

ПРИМЕРЫ СОВЕТОВ И ЗНАЧЕНИЯ ТЕГОВ: 
tag: (тег, совет)
"notag": "⚖️ нейтрально", "Не забудь подготовиться!"
"quiet": "🤫 тихо", "Обрати внимание на своё состояние. Тишина помогает сосредоточиться."
"loud": "🔊 шумно", "Шум может мешать. Попробуй сделать паузу, чтобы перезагрузиться."
"crowd": "👥 много людей", "Если становится тесно, найди момент для короткого перерыва."
"bright": "💡 яркий свет","Свет влияет на настроение. Посмотри в окно, если глаза устают."
"dim": "🌙 тусклый свет", "Вечерний свет приглушает ритм. Хорошее время для отдыха."
"calm": "🧘‍♂️ спокойно", "Насладись моментом тишины и покоя. Он помогает восстановить баланс."

ПРИМЕРЫ:
Активность: "Уроки математики в классе"
Тег: crowd
Если чувствуешь перегрузку от одноклассников, попробуй 2 минуты смотреть в окно или глубоко вдохнуть.

Активность: "Домашняя работа за компьютером"
Тег: bright
Каждые 20 минут отводи взгляд от экрана на 20 секунд — это снизит нагрузку на глаза.

Активность: "Прогулка в парке вечером"
Тег: calm
Насладись моментом тишины — глубокое дыхание поможет закрепить спокойное состояние.

ТЕКУЩИЙ ЗАПРОС:
Активность: "{activity}"
Тег: {tag}
"""

    async def get_advice(self, activity: str, tag: str) -> Tuple[str, bool]:
        if not activity.strip() or len(activity) > 100:
            return TAGS.get(tag, TAGS["notag"]), False
        
        if not self._client:
            return TAGS.get(tag, TAGS["notag"]), False
        
        try:
            messages = [{"role": "user", "text": self._get_prompt(activity, tag)}]
            completion = await wait_for(
                self._client.get_async_completion(messages=messages),
                timeout=10.0
            )
            advice = completion.strip()
            
            if not advice or not (5<len(advice)<200):
                return TAGS.get(tag, TAGS["notag"]), False
            
            return (advice, TAGS.get(tag, TAGS["notag"][0])[0]), True
        except (TimeoutError, Exception) as e:
            logger.warning(f"YandexGPT ERROR ({type(e).__name__})")
            return TAGS.get(tag, TAGS["notag"]), False
