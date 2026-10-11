import time

from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramForbiddenError

from filters.chat_type import ChatTypeFilter
from lg_messages.func import lg_check4_lg_id
from tools.db_conn import cur, conn, collection
from tools.time_file import timefunc
from tools.mongo_queries import *
from data_small import admins, group


router = Router()


class UpdateState(StatesGroup):
    state_one = State()
    state_two = State()
    state_three = State()


class NewsletterState(StatesGroup):
    state_one = State()
    state_two = State()
    state_three = State()


class AboutState(StatesGroup):
    state_one = State()
    state_two = State()
    state_three = State()


# @router.message(Command('list'))
# async def list_enter(message: Message, state: FSMContext, dialog_manager: DialogManager):
#     await message.answer('started')
#     await dialog_manager.start(ListState.start, mode=StartMode.RESET_STACK)
@router.message(Command('select'))
async def select_mongo(message: Message):
    await message.answer('ok')


@router.message(Command('test'))
async def test(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('test1')


@router.message(Command('admin'), F.chat.id == 736978777)
async def admin_update(message: Message):
    cur.execute('SELECT user_id FROM admins')
    admins_db = cur.fetchone()
    admin_id = int(admins_db[0])
    admins.clear()
    admins.append(admin_id)
    print(admins)
    await message.answer("OK")


@router.message(Command('admin_add4196'))
async def admins_add(message: Message):
    cur.execute('INSERT INTO admins (user_id, name, username) VALUES (%s, %s, %s)',
                (message.from_user.id, message.from_user.first_name, message.from_user.username))
    conn.commit()
    await message.answer('Added\n/admin')


@router.message(Command('update'), F.chat.id == group)
async def version(message: Message, state: FSMContext):
    version_id = message.text.split('\n')[1]
    version_data = {'v': version_id}
    await state.set_state(UpdateState.state_one)
    await state.set_data(version_data)
    await message.answer('ok')


@router.message(F.chat.id == group, UpdateState.state_one)
async def version_handler1(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO sets (date, version, version_description) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.set_state(UpdateState.state_two)


@router.message(F.chat.id == group, UpdateState.state_two)
async def version_handler2(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO sets (date, version, version_description) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.set_state(UpdateState.state_three)


@router.message(F.chat.id == group, UpdateState.state_three)
async def version_handler3(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO sets (date, version, version_description) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.clear()


@router.message(Command('send'), F.chat.id.in_(admins))
async def send_update(message: Message, bot: Bot):
    cur.execute('SELECT * FROM sets ORDER BY id DESC LIMIT 3')
    result = cur.fetchall()
    result_uz = result[0]
    result_ru = result[1]
    result_en = result[2]
    version_id = result_uz[2]
    update_msg_id_en = int(result_en[3])
    update_msg_id_ru = int(result_ru[3])
    update_msg_id_uz = int(result_uz[3])

    cur.execute('SELECT * FROM users WHERE status = 1')
    users_all = cur.fetchall()
    for user in users_all:
        time.sleep(1)
        try:
            await bot.send_message(user[3], lg_check4_lg_id(
                f"<b>Bot updated: {version_id}</b>",
                f"<b>Обновление Бота: {version_id}</b>",
                f"<b>Bot Yangilanishi: {version_id}</b>",
                user[6]
            ), parse_mode='html')
            if user[6] == 'en':
                await bot.copy_message(user[3], group, update_msg_id_en)
            elif user[6] == 'ru':
                await bot.copy_message(user[3], group, update_msg_id_ru)
            elif user[6] == 'uz':
                await bot.copy_message(user[3], group, update_msg_id_uz)
            else:
                await bot.copy_message(user[3], group, update_msg_id_en)
                await message.answer('ERROR')
            # cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (1, f"{user[3]}"))
            # conn.commit()
            # print('status set 1')
        except TelegramForbiddenError as e:
            await message.answer(f"{e} - {user[0]}")
            cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (0, f"{user[3]}"))
            conn.commit()
        except Exception as e2:
            await message.answer(f"{e2}")
        await message.answer(f"{user[1]} - @{user[2]}\nid: {user[3]}")


@router.message(Command('send2'), F.chat.id.in_(admins))
async def send_update2(message: Message, bot: Bot):
    cur.execute('SELECT * FROM sets ORDER BY id DESC LIMIT 3')
    result = cur.fetchall()
    result_uz = result[0]
    result_ru = result[1]
    result_en = result[2]
    version_id = result_uz[2]
    update_msg_id_en = int(result_en[3])
    update_msg_id_ru = int(result_ru[3])
    update_msg_id_uz = int(result_uz[3])

    cur.execute("SELECT * FROM users WHERE status IS NULL")
    users_all = cur.fetchall()
    for user in users_all:
        time.sleep(1)
        try:
            await bot.send_message(user[3], lg_check4_lg_id(
                f"<b>Bot updated: {version_id}</b>",
                f"<b>Обновление Бота: {version_id}</b>",
                f"<b>Bot Yangilanishi: {version_id}</b>",
                user[6]
            ), parse_mode='html')
            if user[6] == 'en':
                await bot.copy_message(user[3], group, update_msg_id_en)
            elif user[6] == 'ru':
                await bot.copy_message(user[3], group, update_msg_id_ru)
            elif user[6] == 'uz':
                await bot.copy_message(user[3], group, update_msg_id_uz)
            else:
                await bot.copy_message(user[3], group, update_msg_id_en)
                await message.answer('ERROR')
            cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (1, f"{user[3]}"))
            conn.commit()
            print('status set 1')
        except TelegramForbiddenError as e:
            await message.answer(f"{e} - {user[0]}")
            cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (0, f"{user[3]}"))
            conn.commit()
        except Exception as e2:
            await message.answer(f"{e2}")
        await message.answer(f"{user[1]} - @{user[2]}\nid: {user[3]}")


@router.message(Command('about_update'), F.chat.id == group)
async def about_update(message: Message, state: FSMContext):
    version_id = message.text.split('\n')[1]
    about_data = {'v': version_id}
    await state.set_state(AboutState.state_one)
    await state.set_data(about_data)
    await message.answer('ok')


@router.message(F.chat.id == group, AboutState.state_one)
async def about_handler1(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO abouts (date, version, msg) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.set_state(AboutState.state_two)


@router.message(F.chat.id == group, AboutState.state_two)
async def about_handler(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO abouts (date, version, msg) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.set_state(AboutState.state_three)


@router.message(F.chat.id == group, AboutState.state_three)
async def about_handler3(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO abouts (date, version, msg) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.clear()


@router.message(Command('chat_action'), F.chat.id.in_(admins))
async def check_chat_action(message: Message, bot: Bot):
    print('start')
    cur.execute('SELECT * FROM users')
    users_all = cur.fetchall()
    for user in users_all:
        time.sleep(1)
        try:
            await bot.send_chat_action(int(user[3]), 'typing')
            cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (1, f"{user[3]}"))
            conn.commit()
            await message.answer(f'ok - {user[3]}')
        except TelegramForbiddenError as e:
            cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (0, f"{user[3]}"))
            conn.commit()
            await message.answer(f"{e} - {user[3]}")


@router.message(ChatTypeFilter(chat_type='group'), F.document)
async def handle_document(message: Message):
    file_id = message.document.file_id
    print(f"{message.document.file_name}: {file_id}")


@router.message(ChatTypeFilter(chat_type='group'), F.text, F.chat.id.in_(admins))
async def text_handler(message: Message):
    await message.answer(f"{message.chat.id}")
    print(message.message_id)


@router.message(Command('send_now'), F.chat.id.in_(admins))
async def sender(message: Message, bot: Bot):
    message_lines = message.text.split('\n')[1:]
    message_text = '\n'.join(message_lines)
    cur.execute('SELECT * FROM users WHERE status = 1')
    users_all = cur.fetchall()
    for user in users_all:
        time.sleep(1)
        try:
            await bot.send_message(user[3], message_text)
        except Exception as e:
            await message.answer(f"{e} - {user[0]}")
        await message.answer(f"{user[1]} - @{user[2]}\nid: {user[3]}")


@router.message(Command('mongo_delete'), F.chat.id.in_(admins)) # mongo coin zero
async def mongo_delete(message: Message):
    cur.execute('SELECT tg_id FROM users')
    users_all = cur.fetchone()
    for user in users_all:
        for book in range(1, 7):
            for unit in range(1, 31):
                result = update_result_checker(update_coins(int(user), book, unit, 0))
                print(result)
    await message.answer('updated')


@router.message(Command('mongo'), F.chat.id.in_(admins)) # copy all users from pg to mongo
async def mongo_all_add(message: Message):
    cur.execute('SELECT tg_id FROM users')
    users_all = cur.fetchall()
    for user in users_all:
        user = int(user[0])
        print(user)
        insert_new(user)
    await message.answer('added')


@router.message(Command('zero_coin'), F.chat.id.in_(admins))
async def coin_zero(message: Message):
    new_value = 0
    update_query = """
    UPDATE users
    SET rank = %s;
    """
    try:
        cur.execute(update_query, (new_value,))
        conn.commit()
        print("Все записи успешно обновлены.")
    except Exception as e:
        conn.rollback()
        print(f"Произошла ошибка: {e}")
    await message.answer('ok')


@router.message(Command('select_mongo'))
async def select_mongo(message: Message):
    result = select_coin(message.from_user.id, 1, 1)
    print(result)
    await message.answer('ok')


@router.message(Command('invite_add'), F.chat.id.in_(admins))
async def invite_db_check(message: Message):
    cur.execute('SELECT tg_id FROM users WHERE status = 1')
    users_all = cur.fetchall()
    for user in users_all:
        user_id = int(user[0])
        result = select_invite(user_id)
        if result is None:
            insert_new_invite(user_id)
            await message.answer(f"{user_id}")
            time.sleep(1)
    await message.answer('ok')


@router.message(Command('newsletter'), F.chat.id == group)
async def newsletter(message: Message, state: FSMContext):
    version_id = message.text.split('\n')[1]
    version_data = {'v': version_id}
    await state.set_state(NewsletterState.state_one)
    await state.set_data(version_data)
    await message.answer('ok')


@router.message(F.chat.id == group, NewsletterState.state_one)
async def version_news_handler1(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO space (date, ver_id, msg_id) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.set_state(NewsletterState.state_two)


@router.message(F.chat.id == group, NewsletterState.state_two)
async def version_news_handler2(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO space (date, ver_id, msg_id) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.set_state(NewsletterState.state_three)


@router.message(F.chat.id == group, NewsletterState.state_three)
async def version_news_handler3(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    version_id = data.get('v')
    today = timefunc('today')
    time = timefunc('time')
    today_time = f'{today}/{time}'
    msg_id = message.message_id
    cur.execute('INSERT INTO space (date, ver_id, msg_id) VALUES (%s, %s, %s)',
                (today_time, version_id, msg_id))
    conn.commit()
    await bot.copy_message(message.from_user.id, group, msg_id)
    await state.clear()


@router.message(Command('send_news'), F.chat.id.in_(admins))
async def send_news(message: Message, bot: Bot):
    cur.execute('SELECT * FROM space ORDER BY id DESC LIMIT 3')
    result = cur.fetchall()
    result_uz = result[0]
    result_ru = result[1]
    result_en = result[2]
    version_id = result_uz[2]
    update_msg_id_en = int(result_en[3])
    update_msg_id_ru = int(result_ru[3])
    update_msg_id_uz = int(result_uz[3])

    cur.execute('SELECT * FROM users WHERE status = 1')
    users_all = cur.fetchall()
    for user in users_all:
        time.sleep(1)
        try:
            if user[6] == 'en':
                await bot.copy_message(user[3], group, update_msg_id_en)
            elif user[6] == 'ru':
                await bot.copy_message(user[3], group, update_msg_id_ru)
            elif user[6] == 'uz':
                await bot.copy_message(user[3], group, update_msg_id_uz)
            else:
                await bot.copy_message(user[3], group, update_msg_id_en)
                await message.answer('ERROR')
            # cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (1, f"{user[3]}"))
            # conn.commit()
            # print('status set 1')
        except TelegramForbiddenError as e:
            await message.answer(f"{e} - {user[0]}")
            cur.execute('UPDATE users SET status = %s WHERE tg_id = %s', (0, f"{user[3]}"))
            conn.commit()
        except Exception as e2:
            await message.answer(f"{e2}")
        await message.answer(f"{user[1]} - @{user[2]}\nid: {user[3]}")


@router.message(Command('test2'), F.chat.id.in_(admins))
async def test_msg(message: Message):
    await message.answer('test')

