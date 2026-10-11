from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply import row1, language_selection
from tools.db_conn import fetch_all
from utils.states import Profile, Form
from data_small import *
from dialogs.funcs_dialog import TOP_SIZE
from lg_messages.func import lg_check
from funcs import bot_version, invite_link

router = Router()


@router.message(Profile.profile_start, F.text.in_(version_btn_all))
async def version_info(message: Message, bot: Bot):
    await bot_version(message, bot)


@router.message(Profile.profile_start, F.text.in_(lang_change_btn_all))
async def language_choose(message: Message, state: FSMContext):
    await state.set_state(Form.language)
    await message.answer(text=lg_check('Choose language',
                                       'Выберите язык',
                                       'Til tanlang', message),
                         reply_markup=language_selection(lg_check(languages_en,
                                                                  languages_ru,
                                                                  languages_uz,
                                                                  message)))


@router.message(Profile.profile_start, F.text.in_(rating_btn_all))
async def top_users(message: Message, state: FSMContext):
    result = fetch_all('SELECT name, username, tg_id, rank FROM users WHERE status = 1 '
                       'ORDER BY CASE WHEN rank IS NULL THEN 1 ELSE 0 END, rank DESC')

    creator_text = lg_check("👨🏻‍💻 Admin", "👨🏻‍💻 Админ", "👨🏻‍💻 Admin", message)
    you_text = lg_check("You", "Вы", "Siz", message)

    def row_text(place, row):
        name, username, tg_id, rank = row
        handle = f" - @{username}" if username else ''
        mark = ''
        if tg_id in admins:
            mark = f" <i>({creator_text})</i>"
        elif tg_id == message.from_user.id:
            mark = f" <i>({you_text})</i>"
        return f"<b>{place}.</b> {name}{handle}: <b>{rank or 0} coins</b>{mark}\n"

    top_text = ''
    my_place = None
    for place, row in enumerate(result, 1):
        if row[2] == message.from_user.id:
            my_place = place
        if place <= TOP_SIZE:
            top_text += row_text(place, row)

    # a user outside the top still gets to see their own line
    if my_place and my_place > TOP_SIZE:
        top_text += '\n' + row_text(my_place, result[my_place - 1])

    msg_text = (f"📊 <b>{lg_check(f'TOP {TOP_SIZE} Users', f'ТОП {TOP_SIZE} Пользователей', f'TOP {TOP_SIZE} Userlar', message)}:</b>\n\n"
                f"{top_text}\n"
                "@essentialwordstestbot")
    kb = row1([lg_check("🔙 Back", "🔙 Назад", "🔙 Orqaga", message),
               lg_check("🏠 Main Menu", "🏠 Главное Меню", "🏠 Asosiy Menyu", message)])
    await state.set_state(Profile.rating)
    await message.answer(msg_text, reply_markup=kb)
    await message.answer(lg_check(
        "📢 Subscribe to our channel so you don't miss competitions:👇\n@essentialwordchannel",
        "📢 Подпишитесь на наш канал чтобы не пропустить конкурсы:👇\n@essentialwordchannel",
        "📢 Musobaqalarni o'tkazib yubormaslik uchun kanalimizga obuna bo'ling:👇\n@essentialwordchannel",
        message))


@router.message(Profile.profile_start, F.text.in_(invite_btn_all))
async def invite_profile(message: Message, bot: Bot):
    await invite_link(message, bot)
