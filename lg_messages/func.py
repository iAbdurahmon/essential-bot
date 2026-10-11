from aiogram.types import Message, User

from tools.db_conn import fetch_one

# A reply is built from a dozen translated strings and every one of them used to cost
# a SELECT. The language of a user changes only through the handlers below, so it is
# cached here and dropped explicitly when it does.
_lang_cache = {}


def lg_checker2(user_id):
    user_id = int(user_id)
    if user_id not in _lang_cache:
        row = fetch_one('SELECT lg FROM users WHERE tg_id = %s', (user_id,))
        _lang_cache[user_id] = row[0] if row else None
    return _lang_cache[user_id]


def drop_lang_cache(user_id):
    _lang_cache.pop(int(user_id), None)


def lg_check4_lg_id(eng, rus, uzb, lg):
    if lg == 'ru':
        return rus
    if lg == 'uz':
        return uzb
    return eng


def lg_check(eng, rus, uzb, message: Message):
    lg = lg_checker2(message.from_user.id) or message.from_user.language_code
    return lg_check4_lg_id(eng, rus, uzb, lg)


def lg_check3(eng, rus, uzb, from_user: User):
    lg = lg_checker2(from_user.id) or from_user.language_code
    return lg_check4_lg_id(eng, rus, uzb, lg)
