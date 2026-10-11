import asyncio
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.scene import SceneRegistry
from aiogram_dialog import setup_dialogs
from aiogram.client.default import DefaultBotProperties

import funcs

from config_reader import config
from handlers import *
from Funcs import books
from Poll import polling
from dialogs import dialog, poll, main_poll
from dialogs.main_poll import QuizScene
from middlewares.is_online import IsOnline

LOG_DIR = 'logs'
LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'

logger = logging.getLogger(__name__)


def logging_setup():
    os.makedirs(LOG_DIR, exist_ok=True)
    formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, 'bot.log'),
        when='midnight',
        backupCount=14,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=config.log_level, handlers=[file_handler, console_handler])
    # these two are chatty at DEBUG and say nothing useful at INFO
    logging.getLogger('aiogram.event').setLevel(logging.WARNING)
    logging.getLogger('aiogram_dialog').setLevel(logging.WARNING)


def dp_setup():
    storage = RedisStorage.from_url(config.redis_url, key_builder=DefaultKeyBuilder(with_destiny=True))
    dp = Dispatcher(storage=storage,
                    events_isolation=SimpleEventIsolation())
    dp.message.middleware.register(IsOnline())
    dp.include_routers(all_handler.router,
                       start.router,
                       back_handlers.router,
                       user_commands.router,
                       config_handlers.router,
                       funcs.router,
                       books.router,
                       polling.router,
                       translator.router,
                       profile.router,
                       word_list.router,
                       dialog.dialog,
                       poll.dialog,
                       main_poll.router_poll)
    setup_dialogs(dp)
    scene_registry = SceneRegistry(dp)
    scene_registry.add(QuizScene)
    return dp


async def main():
    dp = dp_setup()
    bot = Bot(
        token=config.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode='HTML')
    )
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info('bot started')
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging_setup()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('bot stopped')
