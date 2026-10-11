from aiogram.filters import Command
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from datetime import datetime, timedelta

from data_small import *
from utils.states import *
from lg_messages.func import lg_check
from handlers.start import start, about
from handlers.profile import top_users, language_choose
from funcs import bot_version, invite_link
from tools.db_conn import cur
from tools.time_file import timefunc

router = Router()


@router.message(Command('language'))
async def language_choose_cm(message: Message, bot: Bot, state: FSMContext):
    await language_choose(message, bot, state)


@router.message(Command('version'))
async def version_command(message: Message, bot: Bot):
    user_info = f"""
#version
Full name: {message.from_user.full_name}
ID: {message.from_user.id}
Username: @{message.from_user.username}
    """
    await bot.send_message(group, user_info)
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
async def statistics_print(message: Message, bot: Bot):
    user_info = f"""
#statistics
Full name: {message.from_user.full_name}
ID: {message.from_user.id}
Username: @{message.from_user.username}
    """
    await bot.send_message(group, user_info)
    cur.execute('SELECT * FROM users WHERE status = %s', (1,))
    users_all = cur.fetchall()
    db_dates = []
    date_format = "%d.%m.%y"
    today = timefunc('today')
    time_now = timefunc('time')
    today_formatted = datetime.strptime(today, date_format)
    delta = timedelta(days=7)
    seven_days_formatted = today_formatted - delta
    result = []
    for i in range(1, 8):
        seven_days_formatted += timedelta(days=1)
        my_format = seven_days_formatted.strftime(date_format)
        cur.execute("SELECT * FROM users WHERE created_on ILIKE %s", (my_format + '%',))
        result_db = cur.fetchall()
        if result_db:
            db_dates.append(result_db)
        if my_format == today:
            result = [i[4] for i in result_db]
    counter = 0
    for i in db_dates:
        for i2 in i:
            counter += 1
    week_result = counter
    today_result = len(result)
    all_users = len(users_all)

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
    user_info = f"""
#about
Full name: {message.from_user.full_name}
ID: {message.from_user.id}
Username: @{message.from_user.username}
    """
    await bot.send_message(group, user_info)
    await about(message, state, bot)


@router.message(Command('balance'))
async def my_rank(message: Message, bot: Bot):
    cur.execute('SELECT rank FROM users WHERE tg_id = %s', (f"{message.from_user.id}",))
    rank = cur.fetchone()[0]
    if not rank:
        rank = 0
    balance_text = lg_check("Your balance:",
                            "Ваш баланс:",
                            "Sizning balansingiz:", message)
    await message.answer(f"{balance_text} <b>{rank} coin</b>")
    await bot.send_message(group,
                           f"#balance\n"
                           f"<b>{rank}</b>\n"
                           f"{message.from_user.first_name}\n"
                           f"@{message.from_user.username}\n"
                           f"{message.from_user.id}")


@router.message(Command('top10'))
async def top_users_cm(message: Message, bot: Bot, state: FSMContext):
    await top_users(message, bot, state)


@router.message(Command('invite_link'))
async def invite_creator(message: Message, bot: Bot):
    await invite_link(message, bot)
