from aiogram.filters import Command
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Bot

from data_small import *
from utils.states import *
from lg_messages.func import lg_check
from handlers.start import start, about
from handlers.profile import top_users, language_choose
from funcs import bot_version, invite_link
from tools.db_conn import fetch_value
from tools.time_file import timefunc, TIMEZONE

router = Router()

STATS_DAYS = 7


@router.message(Command('language'))
async def language_choose_cm(message: Message, state: FSMContext):
    await language_choose(message, state)


@router.message(Command('version'))
async def version_command(message: Message, bot: Bot):
    await bot_version(message, bot)


@router.message(Command('stop'), Translate.text)
async def translator_stop(message: Message, state: FSMContext):
    await message.answer(
        lg_check("You have exited translator mode!",
                 "Вы вышли из режима переводчика!",
                 "Siz tarjimon rejimidan chiqdingiz!", message)
    )
    await start(message, state)


@router.message(Command('statistics'))
async def statistics_print(message: Message):
    today = timefunc('today')
    time_now = timefunc('time')

    all_users = fetch_value('SELECT COUNT(*) FROM users WHERE status = 1', default=0)
    week_result = fetch_value('SELECT COUNT(*) FROM users '
                              "WHERE created_on >= now() - make_interval(days => %s)",
                              (STATS_DAYS,), default=0)
    # the bot's audience lives in one timezone, so "today" is counted in that one
    today_result = fetch_value('SELECT COUNT(*) FROM users WHERE '
                               '(created_on AT TIME ZONE %s)::date = (now() AT TIME ZONE %s)::date',
                               (TIMEZONE, TIMEZONE), default=0)

    message_text = lg_check(
        "*📊 Statistic:*\n\n"
        f"_👥 Total users:_ *{all_users}*\n"
        f"_📈 In the last seven days:_ *{week_result}*\n"
        f"_🕒 Today:_ *{today_result}*\n"
        f"_📆 Date:_ *{today}/{time_now}*",
        "*📊 Статистика:*\n\n"
        f"_👥 Всего пользователей:_ *{all_users}*\n"
        f"_📈 За последние семь дней:_ *{week_result}*\n"
        f"_🕒 Сегодня:_ *{today_result}*\n"
        f"_📆 Дата:_ *{today}/{time_now}*",
        "*📊 Statistika:*\n\n"
        f"_👥 Jami foydalanuvchilar:_ *{all_users}*\n"
        f"_📈 So'nggi etti kun ichida:_ *{week_result}*\n"
        f"_🕒 Bugun:_ *{today_result}*\n"
        f"_📆 Sana:_ *{today}/{time_now}*", message
    )

    await message.answer(message_text, parse_mode='MARKDOWN')


@router.message(Command('about'))
async def about_command(message: Message, state: FSMContext, bot: Bot):
    await about(message, state, bot)


@router.message(Command('balance'))
async def my_rank(message: Message):
    rank = fetch_value('SELECT rank FROM users WHERE tg_id = %s',
                       (message.from_user.id,), default=0)
    balance_text = lg_check("Your balance:",
                            "Ваш баланс:",
                            "Sizning balansingiz:", message)
    await message.answer(f"{balance_text} <b>{rank} coin</b>")


@router.message(Command('top10'))
async def top_users_cm(message: Message, state: FSMContext):
    await top_users(message, state)


@router.message(Command('invite_link'))
async def invite_creator(message: Message, bot: Bot):
    await invite_link(message, bot)
