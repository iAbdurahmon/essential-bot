from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from keyboards.reply import *
from utils.states import Func1, Profile
from data_small import *
from lg_messages.func import lg_check, lg_checker2
from Poll import polling
from tools.db_conn import cur

router = Router()


@router.message(Func1.choose_option, F.text.in_(book_btn_all))
async def list_book(message: Message, state: FSMContext):
    await message.answer(lg_check("🔘 Choose option <b>(book or list)</b>",
                                  "🔘 Выберите опцию <b>(книга или список)</b>",
                                  "🔘Variantni tanlang <b>(kitob yoki ro'yxat)</b>", message),
                         reply_markup=buttons3(lg_check(btn_b_l_en, btn_b_l_ru, btn_b_l_uz, message), message),
                         parse_mode='html')
    await state.set_state(Func1.choose_book_or_list)


@router.message(Func1.choose_option, F.text.in_(quiz_btn_all))
async def quiz_test(message: Message, state: FSMContext):
    await polling.book(message, state)


@router.message(Func1.choose_option, F.text.in_(profile_btn_all))
async def profile_start(message: Message, state: FSMContext):
    await state.set_state(Profile.profile_start)
    kb = buttons4_2(lg_check(profile_buttons_en,
                             profile_buttons_ru,
                             profile_buttons_uz, message), message)
    await message.answer(lg_check("⚙️ Choose any setting", "⚙️ Выберите любую настройку", "⚙️ Har qanday sozlamani tanlang", message),
                         reply_markup=kb)


@router.message(Func1.choose_book_or_list, F.text.in_(btn_b_l_all), F.text.in_(btn_b_l_book))
async def book(message: Message, state: FSMContext):
    await message.answer(lg_check("🔘 Choose a book:", "🔘 Выберите книгу:", "🔘 Kitobni tanlang:", message),
                         reply_markup=func_kb(lg_check(book_names_en,
                                                       book_names_ru,
                                                       book_names_uz,
                                                       message), message))
    await state.set_state(Func1.choose_book)


@router.message(Func1.choose_book_or_list, F.text.in_(btn_b_l_all), F.text.in_(btn_b_l_list))
async def list(message: Message, bot: Bot):
    await message.answer(lg_check(
        "🛠️ The word list is under development.\nSoon...",
        "🛠️ Список слов находится в разработке.\nСкоро...",
        "🛠️ Soʻzlar roʻyxati ishlab chiqilmoqda.\nTez orada...",
        message
    ))
    text = f"#list\n{message.from_user.username} - {message.from_user.id} - {message.from_user.first_name}"
    await bot.send_message(group, text)


async def bot_version(message: Message, bot: Bot):
    lg = lg_checker2(message.from_user.id)
    cur.execute('SELECT * FROM sets ORDER BY id DESC LIMIT 3')
    result = cur.fetchall()
    result_uz = result[0]
    result_ru = result[1]
    result_en = result[2]
    version_id = result_uz[2]
    update_msg_id_en = int(result_en[3])
    update_msg_id_ru = int(result_ru[3])
    update_msg_id_uz = int(result_uz[3])
    await message.answer(lg_check(
        f"<b>Bot Version: {version_id}</b>",
        f"<b>Версия Бота: {version_id}</b>",
        f"<b>Bot Versiyasi: {version_id}</b>",
        message
    ), parse_mode='html')
    if lg == 'en':
        await bot.copy_message(message.from_user.id, group, update_msg_id_en)
    if lg == 'ru':
        await bot.copy_message(message.from_user.id, group, update_msg_id_ru)
    if lg == 'uz':
        await bot.copy_message(message.from_user.id, group, update_msg_id_uz)


async def invite_link(message: Message, bot: Bot):
    link = await create_start_link(bot, f"{message.from_user.id}", encode=True)
    share_text = (lg_check(
        f"*Your Invite Link: 👇\n\n*"
        f"`{link}`\n\n"
        f"_Tap it for copy 👆 and share with your friends and earn_ *{invite_coin}* 🪙",
        f"*Ваша ссылка для приглашения: 👇\n\n*"
        f"`{link}`\n\n"
        f"_Нажмите чтобы скопировать 👆и поделитесь этим с друзьями и получите_ *{invite_coin}* 🪙",
        f"*Taklif havolangiz: 👇\n\n*"
        f"`{link}`\n\n"
        f"_Kopiya qilish uchun ustini bosing 👆va do'stlaringiz bilan ulashing va_ *{invite_coin}* 🪙 _oling_",
        message
    ))
    await message.answer(share_text, parse_mode='MARKDOWN')
    text = f"#invite\n{message.from_user.username} - {message.from_user.id} - {message.from_user.first_name}"
    await bot.send_message(group, text)
    await bot.send_message(group, share_text, parse_mode='MARKDOWN')


