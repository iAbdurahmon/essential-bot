from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link

from keyboards.reply import *
from utils.states import Func1, Profile
from data_small import *
from lg_messages.func import lg_check, lg_checker2
from Poll import polling
from tools.posts import last_post

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


async def bot_version(message: Message, bot: Bot):
    version, msg_ids = last_post('sets')
    if not msg_ids:
        await message.answer(lg_check('No changelog published yet.',
                                      'Список изменений ещё не опубликован.',
                                      "O'zgarishlar ro'yxati hali chiqmagan.", message))
        return
    await message.answer(lg_check(
        f"<b>Bot Version: {version}</b>",
        f"<b>Версия Бота: {version}</b>",
        f"<b>Bot Versiyasi: {version}</b>",
        message
    ), parse_mode='html')
    lg = lg_checker2(message.from_user.id)
    await bot.copy_message(message.from_user.id, group, msg_ids.get(lg, msg_ids['en']))


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


