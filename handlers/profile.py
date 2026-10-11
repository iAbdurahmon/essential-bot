from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.reply import row1, language_selection
from tools.db_conn import cur
from utils.states import Profile, Form
from data_small import *
from lg_messages.func import lg_check
from funcs import bot_version, invite_link

router = Router()


@router.message(Profile.profile_start, F.text.in_(version_btn_all))
async def version_info(message: Message, bot: Bot):
    await bot_version(message, bot)


@router.message(Profile.profile_start, F.text.in_(lang_change_btn_all))
async def language_choose(message: Message, bot: Bot, state: FSMContext):
    user_info = f"""
#language
Full name: {message.from_user.full_name}
ID: {message.from_user.id}
Username: @{message.from_user.username}
    """
    await bot.send_message(group, user_info)
    await state.set_state(Form.language)
    await message.answer(text=lg_check('Choose language',
                                       'Выберите язык',
                                       'Til tanlang', message), reply_markup=language_selection(lg_check(languages_en,
                                                                                                         languages_ru,
                                                                                                         languages_uz,
                                                                                                         message)))


@router.message(Profile.profile_start, F.text.in_(rating_btn_all))
async def top_users(message: Message, bot: Bot, state: FSMContext):
    user_info = f"""
#top10
Full name: {message.from_user.full_name}
ID: {message.from_user.id}
Username: @{message.from_user.username}
        """
    await bot.send_message(group, user_info)
    cur.execute('SELECT * FROM users WHERE status = 1 ORDER BY CASE WHEN rank IS NULL THEN 1 ELSE 0 END, rank DESC')
    result = cur.fetchall()
    top_text = ''
    creator_text = lg_check("👨🏻‍💻 Admin", "👨🏻‍💻 Админ", "👨🏻‍💻 Admin", message)
    you_text = lg_check("You", "Вы", "Siz", message)
    subs_text = lg_check("📢 Subscribe to our channel so you don't miss competitions:👇\n@essentialwordchannel",
                         "📢 Подпишитесь на наш канал чтобы не пропустить конкурсы:👇\n@essentialwordchannel",
                         "📢 Musobaqalarni o'tkazib yubormaslik uchun kanalimizga obuna bo'ling:👇\n@essentialwordchannel",
                         message)
    tg_ids_top = []
    for num, i in enumerate(result):
        tg_ids_top.append(i[3])
        username = f" - @{i[2]}" if i[2] is not None else ''
        balance = i[-1] if i[-1] is not None else 0
        if i[3] != "736978777" and i[3] != str(message.from_user.id):
            top_text += f"<b>{num + 1}.</b> {i[1]}{username}: <b>{balance} coins</b>\n"
        elif i[3] == "736978777":
            top_text += f"<b>{num + 1}.</b> {i[1]}{username}: <b>{balance} coins</b> <i>({creator_text})</i>\n"
        elif i[3] == str(message.from_user.id):
            top_text += f"<b>{num + 1}.</b> {i[1]}{username}: <b>{balance} coins</b> <i>({you_text})</i>\n"
        if num + 1 == 10:
            break

    if str(message.from_user.id) not in tg_ids_top:
        for num2, i2 in enumerate(result):
            username = f" - @{i2[2]}" if i2[2] is not None else ''
            balance = i2[-1] if i2[-1] is not None else 0

            if i2[3] == str(message.from_user.id):
                my_rank = f"\n<b>{num2 + 1}.</b> {i2[1]}{username}: <b>{balance} coins</b> <i>({you_text})</i>\n"

                top_text += my_rank
    msg_text = (f"📊 <b>{lg_check('TOP 10 Users', 'ТОП 10 Пользователей', 'TOP 10 Userlar', message)}:</b>\n\n"
                f"{top_text}\n"
                "@essentialwordstestbot")
    kb = row1([lg_check("🔙 Back", "🔙 Назад", "🔙 Orqaga", message),
              lg_check("🏠 Main Menu", "🏠 Главное Меню", "🏠 Asosiy Menyu", message)])
    await state.set_state(Profile.rating)
    await message.answer(msg_text, reply_markup=kb)
    await message.answer(subs_text)


@router.message(Profile.profile_start, F.text.in_(invite_btn_all))
async def invite_profile(message: Message, bot: Bot):
    await invite_link(message, bot)
