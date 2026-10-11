from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext

from data_small import *
from utils.states import Func1, WordList
from lg_messages.func import lg_check3, lg_checker2
from keyboards.reply import func_kb2
from keyboards.builders import units_inline
from tools.db_conn import fetch_all

router = Router()

MESSAGE_LIMIT = 3500


async def send_book_choice(message: Message, user: User, state: FSMContext):
    await message.answer(lg_check3("🔘 Choose a book:", "🔘 Выберите книгу:", "🔘 Kitobni tanlang:", user),
                         reply_markup=func_kb2(lg_check3(book_names_en,
                                                         book_names_ru,
                                                         book_names_uz, user), user))
    await state.set_state(WordList.choose_book)


@router.message(Func1.choose_book_or_list, F.text.in_(btn_b_l_all), F.text.in_(btn_b_l_list))
async def list_start(message: Message, state: FSMContext):
    await send_book_choice(message, message.from_user, state)


@router.message(WordList.choose_book, F.text.in_(book_names_all))
async def list_units(message: Message, state: FSMContext):
    book = message.text[-1]
    await state.set_state(WordList.choose_unit)
    await message.answer(lg_check3(f"📖 Book {book}. Choose a unit:",
                                   f"📖 Книга {book}. Выберите unit:",
                                   f"📖 Kitob {book}. Unitni tanlang:", message.from_user),
                         reply_markup=units_inline(book, lg_check3("🔙 Back", "🔙 Назад", "🔙 Orqaga",
                                                                   message.from_user)))


@router.callback_query(WordList.choose_unit, F.data == 'wl:back')
async def list_back(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await send_book_choice(callback.message, callback.from_user, state)
    await callback.answer()


@router.callback_query(WordList.choose_unit, F.data.startswith('wl:'))
async def list_words(callback: CallbackQuery):
    book, unit = callback.data.split(':')[1:]
    lg = lg_checker2(callback.from_user.id) or 'en'
    translation = lg_reductions.get(lg, 'eng')

    # eng is always the left side: the bot teaches English through the user's own language
    rows = fetch_all(f"SELECT eng, {translation} FROM book{book} WHERE unit = %s ORDER BY id", (unit,))
    if not rows:
        await callback.answer(lg_check3("There are no words for this unit yet.",
                                        "Для этого unit пока нет слов.",
                                        "Bu unit uchun hozircha so'zlar yo'q.",
                                        callback.from_user), show_alert=True)
        return

    chunk = lg_check3(f"📋 <b>Book {book}, Unit {unit}</b>\n\n",
                      f"📋 <b>Книга {book}, Unit {unit}</b>\n\n",
                      f"📋 <b>Kitob {book}, Unit {unit}</b>\n\n", callback.from_user)

    # a long unit does not fit into a single Telegram message
    for num, (word, meaning) in enumerate(rows, 1):
        line = f"<b>{num}.</b> {word} — {meaning or '—'}\n"
        if len(chunk) + len(line) > MESSAGE_LIMIT:
            await callback.message.answer(chunk)
            chunk = ''
        chunk += line
    await callback.message.answer(chunk)
    await callback.answer()
