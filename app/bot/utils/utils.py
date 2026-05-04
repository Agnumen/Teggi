from typing import Dict, Any
import asyncio
import logging

from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.exceptions import (
    TelegramForbiddenError,
    TelegramBadRequest,
    TelegramRetryAfter,
    TelegramNotFound,
)

from app.infrastructure.database import Database

logger = logging.getLogger(__name__)

MESSAGE_DELAY = 0.05   # 50 мс -> ~20 сообщений/сек

def get_content_info(message: Message) -> Dict[str, Any]:
    content_type = None
    file_id = None

    if message.photo:
        content_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        content_type = "video"
        file_id = message.video.file_id
    elif message.audio:
        content_type = "audio"
        file_id = message.audio.file_id
    elif message.document:
        content_type = "document"
        file_id = message.document.file_id
    elif message.voice:
        content_type = "voice"
        file_id = message.voice.file_id
    elif message.text:
        content_type = "text"

    content_text = message.text or message.caption
    return {'content_type': content_type, 'file_id': file_id, 'content_text': content_text}

async def send_message_user(bot, user_id, content_type, content_text=None, file_id=None, kb=None) -> None:
    match content_type:
        case 'text': 
            await bot.send_message(chat_id=user_id, text=content_text, reply_markup=kb)
        case 'photo': 
            await bot.send_photo(chat_id=user_id, photo=file_id, caption=content_text, reply_markup=kb)
        case 'document': 
            await bot.send_document(chat_id=user_id, document=file_id, caption=content_text, reply_markup=kb)
        case 'video': 
            await bot.send_video(chat_id=user_id, video=file_id, caption=content_text, reply_markup=kb)
        case 'audio': 
            await bot.send_audio(chat_id=user_id, audio=file_id, caption=content_text, reply_markup=kb)
        case 'voice': 
            await bot.send_voice(chat_id=user_id, voice=file_id, caption=content_text, reply_markup=kb)

async def send_many_messages(
    bot: Bot,
    db: Database,
    content_type: str,
    content_text: str | None = None,
    file_id: str | None = None,
    kb: InlineKeyboardMarkup | ReplyKeyboardMarkup | None = None,
    delay: float = MESSAGE_DELAY,
    mark_blocked: bool = True,
):
    """
    Универсальная массовая рассылка активным пользователям.
    Поддерживает все типы сообщений, обрабатываемые send_message_user.
    """
    user_ids = await db.user.get_active_user_ids()
    logger.info("Starting broadcast to %d users (type=%s)", len(user_ids), content_type)

    sent = 0
    blocked = 0
    errors = 0

    for idx, user_id in enumerate(user_ids, start=1):
        if idx % 50 == 0:
            await asyncio.sleep(0)

        try:
            await send_message_user(
                bot, user_id, content_type,
                content_text=content_text,
                file_id=file_id,
                kb=kb,
            )
            sent += 1

        except TelegramForbiddenError:
            logger.warning("User %d blocked the bot, marking inactive", user_id)
            if mark_blocked:
                await db.user.set_inactive(user_id, "User blocked the bot")
            blocked += 1

        except TelegramNotFound:
            logger.warning("User %d not found, marking inactive", user_id)
            if mark_blocked:
                await db.user.set_inactive(user_id, "User not found")
            blocked += 1

        except TelegramRetryAfter as e:
            logger.warning("Flood control for %d, retry after %d sec", user_id, e.retry_after)
            await asyncio.sleep(e.retry_after + 1)
            try:
                await send_message_user(
                    bot, user_id, content_type,
                    content_text=content_text,
                    file_id=file_id,
                    kb=kb,
                )
                sent += 1
            except Exception as retry_exc:
                logger.error("Retry failed for %d: %s", user_id, retry_exc)
                errors += 1

        except TelegramBadRequest as e:
            logger.error("Bad request for %d: %s", user_id, e)
            errors += 1

        except Exception as e:
            logger.exception("Unexpected error sending to %d", user_id)
            errors += 1

        await asyncio.sleep(delay)

    logger.info(
        "Broadcast finished: sent=%d, blocked=%d, errors=%d",
        sent, blocked, errors,
    )