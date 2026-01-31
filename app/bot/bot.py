import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from app.bot.handlers import checkin, common, settings, other
from app.bot.handlers.admin import stats, edit_settings
from app.bot.scheduler.scheduler import setup_scheduler
from app.bot.filters import IsAdmin
from app.bot.middlewares import DatabaseMiddleware, ActivityCounterMiddleware

from config import Settings

logger = logging.getLogger(__name__)

async def main(config: Settings): 

    logging.basicConfig(
        level=config.LOG_LEVEL,
        format=config.LOG_FORMAT,
    )
    
    logger.info("Starting bot")
    
    # Initialize storage object
    redis = Redis(
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        db=config.REDIS_DB_NUM,
        username=config.REDIS_USERNAME,
        password=config.REDIS_PASSWORD
    )
    storage = RedisStorage(redis=redis)
    
    # Initialize bot&dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="html")
    )
    dp = Dispatcher(storage=storage)

    # Initialize engine and session factory for DB
    engine = create_async_engine(url=config.DATABASE_URL) #, echo=True) # DEV
    async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    
    admin_ids = config.BOT_ADMIN_IDS
    scheduler = setup_scheduler(bot, async_sessionmaker)
    
    # Add required objects to workflow_data
    dp.workflow_data.update({
        "bot": bot,
        "scheduler": scheduler,
        "admin_ids": admin_ids,
    })
    
    scheduler.start()
    
    # Подключаем роутеры в нужном порядке
    logger.info("Including routers...")
    dp.include_routers(
        common.router,
        stats.router,
        edit_settings.router,
        settings.router,
        checkin.router,
        other.router,    
    )
    
    # Filters
    logger.info("Including filters...")
    stats.router.message.filter(IsAdmin(admin_ids))
    stats.router.callback_query.filter(IsAdmin(admin_ids))
    edit_settings.router.message.filter(IsAdmin(admin_ids))
    edit_settings.router.callback_query.filter(IsAdmin(admin_ids))
    
    # Middlewares
    logger.info("Including middlewares...")
    dp.update.middleware(DatabaseMiddleware(async_session_maker))
    dp.update.middleware(ActivityCounterMiddleware())
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    