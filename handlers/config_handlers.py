import asyncio
import logging

from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramForbiddenError

from filters.chat_type import ChatTypeFilter
from lg_messages.func import lg_check4_lg_id
from tools.db_conn import fetch_all, execute
from tools.posts import save_post, last_post
from data_small import admins, group

router = Router()
logger = logging.getLogger(__name__)

# the admin posts three versions of the same text, one per language, in this order
POST_LANGUAGES = ['en', 'ru', 'uz']

# command -> table the post is saved into
POST_TABLES = {
    'update': 'sets',
    'about_update': 'abouts',
    'newsletter': 'space',
}

SEND_DELAY = 0.05  # ~20 messages/sec, below the Telegram limit


class PostState(StatesGroup):
    collecting = State()


def active_users():
    return fetch_all('SELECT tg_id, lg, name, username FROM users WHERE status = 1')


async def copy_to_users(message: Message, bot: Bot, users, msg_ids, header=None):
    sent = 0
    blocked = 0
    failed = 0
    for tg_id, user_lg, name, username in users:
        lg = user_lg if user_lg in msg_ids else 'en'
        try:
            if header:
                await bot.send_message(tg_id, lg_check4_lg_id(*header, lg))
            await bot.copy_message(tg_id, group, msg_ids[lg])
            sent += 1
        except TelegramForbiddenError:
            execute('UPDATE users SET status = %s WHERE tg_id = %s', (0, tg_id))
            blocked += 1
        except Exception as e:
            logger.warning('broadcast to %s failed: %s', tg_id, e)
            failed += 1
        await asyncio.sleep(SEND_DELAY)
    await message.answer(f"✅ Sent: {sent}\n🚫 Blocked: {blocked}\n❌ Failed: {failed}")


@router.message(Command(commands=list(POST_TABLES)), F.chat.id == group)
async def post_start(message: Message, command: CommandObject, state: FSMContext):
    if not command.args:
        await message.answer('Usage: /update <version>')
        return
    await state.set_state(PostState.collecting)
    await state.set_data({'table': POST_TABLES[command.command], 'version': command.args, 'step': 0})
    await message.answer(f"Send 3 posts in this order: {', '.join(POST_LANGUAGES)}")


@router.message(PostState.collecting, F.chat.id == group)
async def post_collect(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    step = data['step']
    lg = POST_LANGUAGES[step]
    save_post(data['table'], data['version'], lg, message.message_id)
    await bot.copy_message(message.from_user.id, group, message.message_id)

    if step + 1 == len(POST_LANGUAGES):
        await state.clear()
        await message.answer(f"Saved into `{data['table']}`")
    else:
        await state.update_data(step=step + 1)


@router.message(Command('send'), F.from_user.id.in_(admins))
async def send_update(message: Message, bot: Bot):
    version, msg_ids = last_post('sets')
    if not msg_ids:
        await message.answer('No complete changelog found, run /update first')
        return
    header = (f"<b>Bot updated: {version}</b>",
              f"<b>Обновление Бота: {version}</b>",
              f"<b>Bot Yangilanishi: {version}</b>")
    await copy_to_users(message, bot, active_users(), msg_ids, header)


@router.message(Command('send_news'), F.from_user.id.in_(admins))
async def send_news(message: Message, bot: Bot):
    version, msg_ids = last_post('space')
    if not msg_ids:
        await message.answer('No complete newsletter found, run /newsletter first')
        return
    await copy_to_users(message, bot, active_users(), msg_ids)


@router.message(Command('send_now'), F.from_user.id.in_(admins))
async def sender(message: Message, bot: Bot):
    message_text = '\n'.join(message.text.split('\n')[1:])
    if not message_text:
        await message.answer('Usage: /send_now\n<your text>')
        return
    sent = 0
    failed = 0
    for tg_id, _, _, _ in active_users():
        try:
            await bot.send_message(tg_id, message_text)
            sent += 1
        except Exception as e:
            logger.warning('send_now to %s failed: %s', tg_id, e)
            failed += 1
        await asyncio.sleep(SEND_DELAY)
    await message.answer(f"✅ Sent: {sent}\n❌ Failed: {failed}")


@router.message(Command('chat_action'), F.from_user.id.in_(admins))
async def check_chat_action(message: Message, bot: Bot):
    alive = 0
    blocked = 0
    for (tg_id,) in fetch_all('SELECT tg_id FROM users'):
        try:
            await bot.send_chat_action(tg_id, 'typing')
            execute('UPDATE users SET status = %s WHERE tg_id = %s', (1, tg_id))
            alive += 1
        except TelegramForbiddenError:
            execute('UPDATE users SET status = %s WHERE tg_id = %s', (0, tg_id))
            blocked += 1
        await asyncio.sleep(SEND_DELAY)
    await message.answer(f"✅ Alive: {alive}\n🚫 Blocked: {blocked}")


@router.message(ChatTypeFilter(chat_type='group'), F.document)
async def handle_document(message: Message):
    # the bot serves whole books by file_id, this is how a new one is collected
    await message.answer(f"<code>{message.document.file_id}</code>")
