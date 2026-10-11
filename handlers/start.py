import logging

from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram import Router, Bot
from aiogram.utils.deep_linking import decode_payload

from aiogram_dialog import DialogManager

from dialogs.funcs_dialog import top_all_checker, notify_overtaken
from tools.time_file import timefunc
from tools.posts import last_post
from data_small import *
from lg_messages.start_messages import *
from keyboards.reply import language_selection
from keyboards.reply import main_buttons
from utils.states import Form, Func1
from tools.db_conn import conn, cur
from lg_messages.func import lg_check, lg_checker2, lg_check4_lg_id, drop_lang_cache
from tools.mongo_queries import *

router = Router()
logger = logging.getLogger(__name__)


async def reward_inviter(message: Message, bot: Bot, args: str):
    try:
        inviter_id = int(decode_payload(args))
    except (ValueError, TypeError):
        logger.warning('bad invite payload from %s', message.from_user.id)
        return
    if inviter_id == message.from_user.id:
        return

    # tg_id is stored as text, so the comparison has to be done on a string
    cur.execute('SELECT tg_id FROM users WHERE tg_id = %s', (str(message.from_user.id),))
    if cur.fetchone():
        return

    invited = select_invite(inviter_id)
    if invited is None:
        insert_new_invite(inviter_id)
        invited = []
    if message.from_user.id in invited:
        return

    cur.execute('SELECT rank FROM users WHERE tg_id = %s', (str(inviter_id),))
    row = cur.fetchone()
    if row is None:
        return

    invited.append(message.from_user.id)
    insert_invite(inviter_id, invited)

    before = top_all_checker()
    cur.execute('UPDATE users SET rank = %s WHERE tg_id = %s',
                ((row[0] or 0) + invite_coin, str(inviter_id)))
    conn.commit()
    after = top_all_checker()

    await notify_overtaken(bot, inviter_id, before, after)

    places_before = {tg_id: place for place, tg_id in before.items()}
    places_after = {tg_id: place for place, tg_id in after.items()}
    passed = (places_before.get(inviter_id, 0)) - (places_after.get(inviter_id, 0))

    inviter_lg = lg_checker2(inviter_id)
    passed_text = ''
    if passed > 0:
        passed_text = lg_check4_lg_id(
            f"🏁 Number of users you passed: <b>{passed}</b>\n",
            f"🏁 Количество пользователей, которых вы обошли: <b>{passed}</b>\n",
            f"🏁 Siz o'tib ketgan foydalanuvchilaringiz soni: <b>{passed}</b>\n",
            inviter_lg)

    text_to_ref = lg_check4_lg_id(
        "Someone entered to the bot with your invite link!\n"
        f"You have earned <b>{invite_coin} 🪙</b>\n{passed_text}",
        "Кто-то вошел в бот по вашей пригласительной ссылке!\n"
        f"Вы заработали <b>{invite_coin} 🪙</b>\n{passed_text}",
        "Kimdir taklif havolangiz bilan botga kirdi!\n"
        f"Siz <b>{invite_coin} 🪙</b> oldingiz\n{passed_text}",
        inviter_lg
    )
    try:
        await bot.send_message(inviter_id, text_to_ref)
    except Exception as e:
        logger.warning('could not notify inviter %s: %s', inviter_id, e)


@router.message(CommandStart(deep_link=True))
async def invite_start(message: Message, state: FSMContext, dialog_manager: DialogManager,
                       command: CommandObject, bot: Bot):
    await reward_inviter(message, bot, command.args)
    await dialog_manager.reset_stack()
    await start(message, state)


@router.message(CommandStart())
async def first_start(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await dialog_manager.reset_stack()
    await start(message, state)


async def start(message: Message, state: FSMContext):
    if select_invite(message.from_user.id) is None:
        insert_new_invite(message.from_user.id)

    cur.execute('SELECT lg FROM users WHERE tg_id = %s AND status = 1', (str(message.from_user.id),))
    if cur.fetchone():
        await state.clear()
        await state.set_state(Func1.choose_option)
        await message.answer(text=lg_check('🔘 Select an option',
                                           '🔘 Выберите вариант',
                                           '🔘 Variantni tanlang', message),
                             reply_markup=main_buttons(lg_check(btn_en, btn_ru, btn_uz, message), message))
        return

    await message.answer(text=lg_check(f'👋 Hello <b>{message.from_user.first_name}</b>!',
                                       f'👋 Здравствуйте <b>{message.from_user.first_name}</b>!',
                                       f'👋 Assalomu alaykum <b>{message.from_user.first_name}</b>!', message),
                         parse_mode='html')
    kb = language_selection(lg_check(
        languages_en, languages_ru, languages_uz, message
    ))
    await message.answer(text=choose_mg.get(message.from_user.language_code, choose_mg['en']),
                         reply_markup=kb)
    await state.set_state(Form.language)


@router.message(Form.language)
async def language(message: Message, state: FSMContext, bot: Bot):
    lg_value = lg_db.get(message.text)
    if not lg_value:
        kb = language_selection(lg_check(
            languages_en, languages_ru, languages_uz, message
        ))
        await message.answer(text=choose_mg.get(message.from_user.language_code, choose_mg['en']),
                             reply_markup=kb)
        return

    main_kb = main_buttons(lg_check(btn_en, btn_ru, btn_uz, message), message)
    cur.execute('SELECT lg FROM users WHERE tg_id = %s', (str(message.from_user.id),))
    if cur.fetchone():
        cur.execute('UPDATE users SET lg = %s, status = %s WHERE tg_id = %s',
                    (lg_value, 1, str(message.from_user.id)))
        conn.commit()
        drop_lang_cache(message.from_user.id)
        await message.answer(
            text=lg_check('✅ You have successfully updated the language!',
                          '✅ Вы успешно обновили язык!',
                          "✅ Siz tilni muvaffaqiyatli o'zgartirdingiz", message),
            reply_markup=main_kb
        )
        await state.set_state(Func1.choose_option)
        return

    today_time = f"{timefunc('today')}/{timefunc('time')}"
    cur.execute('INSERT INTO users (name, username, tg_id, created_on, lg, status) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (message.from_user.first_name, message.from_user.username,
                 message.from_user.id, today_time, lg_value, 1))
    conn.commit()
    drop_lang_cache(message.from_user.id)
    insert_new(message.from_user.id)
    await message.answer(text=lg_check('✅ You have successfully selected the language!',
                                       '✅ Вы успешно выбрали язык!',
                                       '✅ Siz tilni muvaffaqiyatli tanladingiz', message),
                         reply_markup=main_kb)
    await about(message, state, bot)


async def about(message: Message, state: FSMContext, bot: Bot):
    version, msg_ids = last_post('abouts')
    if msg_ids:
        lg = lg_checker2(message.from_user.id)
        await bot.copy_message(message.from_user.id, group, msg_ids.get(lg, msg_ids['en']))
    await state.set_state(Func1.choose_option)
