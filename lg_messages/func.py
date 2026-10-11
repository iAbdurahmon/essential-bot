from tools.db_conn import cur, conn
from aiogram.types import Message, User
from lg_messages.start_messages import hello_mg


def lg_check(eng, rus, uzb, message: Message):
    cur.execute('SELECT lg FROM users WHERE tg_id = %s', (str(message.from_user.id),))
    lg = cur.fetchall()
    if not lg:
        lg = message.from_user.language_code
    else:
        for i in lg:
            lg = i[0]
    if lg == 'en':
        return eng
    elif lg == 'ru':
        return rus
    elif lg == 'uz':
        return uzb
    else:
        return f'{hello_mg.get(message.from_user.language_code)}, <b>{message.from_user.first_name}</b>!'


async def lg_check2(eng, rus, uzb, user_info):
    user_id = user_info.id
    first_name = user_info.first_name
    language_code = user_info.language_code
    cur.execute('SELECT lg FROM users WHERE tg_id = %s', (str(user_id),))
    lg = cur.fetchall()
    for i in lg:
        lg = i[0]
    if lg == 'en':
        return eng
    elif lg == 'ru':
        return rus
    elif lg == 'uz':
        return uzb
    else:
        return f'{hello_mg.get(language_code)}, <b>{first_name}</b>!'


def lg_check3(eng, rus, uzb, from_user: User):
    cur.execute('SELECT lg FROM users WHERE tg_id = %s', (str(from_user.id),))
    lg = cur.fetchall()
    for i in lg:
        lg = i[0]
    if lg == 'en':
        return eng
    elif lg == 'ru':
        return rus
    elif lg == 'uz':
        return uzb
    else:
        return f'{hello_mg.get(from_user.language_code)}, <b>{from_user.first_name}</b>!'


def lg_check4_lg_id(eng, rus, uzb, lg):
    if lg == 'en':
        return eng
    elif lg == 'ru':
        return rus
    elif lg == 'uz':
        return uzb


def lg_checker2(user_id):
    cur.execute('SELECT lg FROM users WHERE tg_id = %s', (str(user_id),))
    lg = cur.fetchall()
    lg_user = None
    for i in lg[0]:
        lg_user = i
    return lg_user
