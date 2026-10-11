print('starting')
import os
import asyncio
import logging
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
from data_small import admins
from middlewares.is_online import IsOnline


def dp_setup():
    storage = RedisStorage.from_url('redis://localhost:6379/0', key_builder=DefaultKeyBuilder(with_destiny=True))
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
                       dialog.dialog,
                       poll.dialog,
                       # main_poll.router_poll
                       )
    dp.include_router(main_poll.router_poll)
    # dp.include_router(poll.router)
    setup_dialogs(dp)
    scene_registry = SceneRegistry(dp)
    scene_registry.add(QuizScene)
    return dp


async def main():
    try:
        print('launching main')
        dp = dp_setup()
        bot = Bot(
            token=config.bot_token.get_secret_value(),
            default=DefaultBotProperties(parse_mode='HTML')
        )
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")  # Выведет ошибку в консоль
        logging.exception("Ошибка в боте")  # Запишет в логи



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    def get_filename(filename):
        log_directory = os.path.split(filename)[0]
        date = os.path.splitext(filename)[1][1:]
        filename = os.path.join(log_directory, date)

        if not os.path.exists('{}.log'.format(filename)):
            return '{}.log'.format(filename)
        index = 0
        f = '{}.{}.log'.format(filename, index)
        while os.path.exists(f):
            index += 1
            f = '{}.{}.log'.format(filename, index)
        return f

    file_handler = TimedRotatingFileHandler(filename='logs/debug.log', when='midnight', interval=1, backupCount=0)
    file_handler.suffix = '%Y%m%d'
    file_handler.namer = get_filename
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S'))

    logging.getLogger().addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(
        logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s', datefmt='%H:%M:%S'))

    logging.getLogger().addHandler(console_handler)
    asyncio.run(main())
