import operator
import asyncio
import logging
import os

from contextlib import suppress
from typing import Any

from aiogram.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.chat_action import ChatActionSender

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Multiselect, Group, Button, Row, Radio
from aiogram_dialog.widgets.text import Format, Multi, Progress
from aiogram_dialog.widgets.media import StaticMedia

from lg_messages.func import lg_check3
from tools.pdf import pdf_setup
from data_small import *
from keyboards.reply import func_kb2

logger = logging.getLogger(__name__)

# Russian units are translated by hand, only the first two books are ready
RU_READY_BOOKS = ('1', '2')


class Unit(StatesGroup):
    unit_state = State()
    load = State()
    send_file = State()


async def get_data(**kwargs):
    user_info = kwargs.get('event_from_user')
    send_message = lg_check3('📤 Send the Units', "📤 Отправить Unit",
                                   "📤 Unitlarni jo'natish", user_info)
    send_all_message = lg_check3('📗 Send the whole book', '📗 Отправить всю книгу', "📗 Butun kitobni yuborish",
                                       user_info)
    book_message = lg_check3('📖 Book', '📖 Книга', "📖 Kitob", user_info)

    lg_en = lg_check3('English', 'Английский', 'Inglizcha', user_info)
    lg_ru = lg_check3('Russian', 'Русский', 'Ruscha', user_info)
    lg_uz = lg_check3('Uzbek', 'Узбекский', "O'zbekcha", user_info)

    return {"buttons_data": buttons_data,
            "lg": send_message,
            'lg_all': send_all_message,
            "book_name": book_message,
            "lang_check": [(lg_en, 'en'), (lg_ru, 'ru'), (lg_uz, 'uz')]}


async def get_bg_data(dialog_manager: DialogManager, **kwargs):
    user_info = kwargs.get('event_from_user')
    wait_message = lg_check3('⏳ Preparation...', '⏳ Подготовка...', "⏳ Tayyorlanmoqda...", user_info)
    return {
        "progress": dialog_manager.dialog_data.get("progress", 0),
        "wait_mg": wait_message,
        "user_info": user_info
    }


async def send_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.start_data
    return {
        "data": data,
        "units_mg": ', '.join('#u' + str(unit) for unit in data['units']),
        "book_mg": data,
        "book_name_mg": data
    }


async def russian_not_ready(event: CallbackQuery, book: str, lang: str) -> bool:
    if book in RU_READY_BOOKS or lang != 'ru':
        return False
    text = lg_check3(
        "Since we do the Russian translation manually, at the moment only operations from the Book 1 and Book 2 work.\n"
        "Follow the news on the channel: @essentialwordchannel",
        'Так как русский перевод мы делаем вручную, на данный момент только работают операции с первой и второй книги.\n'
        'Следите за новостями на канале: @essentialwordchannel',
        "Rus tiliga tarjimani o'zimiz qilganimiz uchun, hozircha faqat birinchi va ikkinchi kitoblar bilan ishlashingiz mumkin.\n"
        "Yangiliklarni kanalda kuzating: @essentialwordchannel", event.from_user)
    await event.answer(text, show_alert=True)
    return True


async def book_sender(callback: CallbackQuery, button: Button,
                      manager: DialogManager):
    book_name = manager.start_data['book']
    lang = manager.find('lang').get_checked()
    if await russian_not_ready(callback, book_name, lang):
        return

    book_ids = {'en': book_ids_en, 'ru': book_ids_ru, 'uz': book_ids_uz}[lang]
    book_id = book_ids.get(int(book_name))
    if not book_id:
        await callback.answer('This book is not uploaded yet.', show_alert=True)
        return
    await callback.message.answer_document(book_id)


async def ok_button(event: CallbackQuery, button: Button,
                    manager: DialogManager):
    book = manager.start_data['book']
    lang = manager.find('lang').get_checked()
    if await russian_not_ready(event, book, lang):
        return

    checked = manager.find('units').get_checked()
    if not checked:
        unit_error = lg_check3("❌ Please select at least one unit!",
                                     "❌ Пожалуйста, выберите хотя бы один unit",
                                     "❌ Iltimos, kamida bitta unit'ni tanlang",
                                     event.from_user)
        await event.answer(unit_error, show_alert=True)
        return

    user_id = event.from_user.id
    await manager.switch_to(Unit.load)
    await manager.update({'progress': 30})

    # merging a few dozen PDF pages is CPU-bound, a thread keeps the bot responsive
    try:
        file_name = await asyncio.to_thread(pdf_setup, checked, book, lang, user_id)
    except FileNotFoundError:
        logger.warning('missing unit file for book %s, lang %s, units %s', book, lang, checked)
        await event.answer('Some of these units are not uploaded yet.', show_alert=True)
        await manager.done()
        return
    await manager.update({'progress': 80})

    menu_msg_id = manager.start_data.get('menu_msg_id')
    if menu_msg_id:
        with suppress(TelegramBadRequest):
            await event.bot.delete_message(event.message.chat.id, menu_msg_id)

    back_menu = lg_check3(back_menu_en, back_menu_ru, back_menu_uz, event.from_user)
    data_dict = {'path': file_name,
                 'book': book,
                 'units': checked,
                 'book_name': lg_check3('Book', 'Книга', 'Kitob', event.from_user)}
    await manager.update({'progress': 100})

    send_mg = await event.message.answer(
        lg_check3('📤 Sending...', '📤 Отправка...', "📤 Jo'natilmoqda...", event.from_user),
        reply_markup=func_kb2(back_menu, event.from_user))
    await manager.done()
    async with ChatActionSender.upload_document(bot=event.bot, chat_id=event.message.chat.id):
        await manager.start(Unit.send_file, data=data_dict)
    with suppress(TelegramBadRequest):
        await event.bot.delete_message(event.message.chat.id, send_mg.message_id)

    await event.message.answer(lg_check3('🔘 Choose button', '🔘 Выберите кнопку', "🔘 Tugmani bosing", event.from_user),
                               reply_markup=func_kb2(back_menu, event.from_user))
    with suppress(OSError):
        os.remove(file_name)


async def on_dialog_start(start_data: Any, dialog_manager: DialogManager):
    await dialog_manager.find('lang').set_checked('en')


dialog = Dialog(
    Window(
        Format('{book_name} {start_data[book]}:'),
        Radio(
            Format("🔘 {item[0]}"),
            Format("⚪️ {item[0]}"),
            id='lang',
            item_id_getter=operator.itemgetter(1),
            items="lang_check"
        ),
        Group(
            Multiselect(
                Format("✅ {item[0]}"),
                Format("{item[0]}"),
                id='units',
                item_id_getter=operator.itemgetter(1),
                items="buttons_data"
            ),
            width=3
        ),
        Row(
            Button(Format("{lg_all}"), id='send_all', on_click=book_sender),
            Button(Format("{lg}"), id='ok', on_click=ok_button),
        ),
        state=Unit.unit_state,
        getter=get_data
    ),
    Window(
        Multi(
            Format("{wait_mg}"),
            Progress("progress", 10),
        ),
        state=Unit.load,
        getter=get_bg_data,
    ),
    Window(
        Format('#{book_name_mg[book_name]}{book_mg[book]}\n'
               'Units: {units_mg}\n'
               '\n'
               '@essentialwordstestbot'),
        StaticMedia(
            path=Format("{data[path]}"),
            type=ContentType.DOCUMENT
        ),
        state=Unit.send_file,
        getter=send_getter
    ),
    on_start=on_dialog_start
)
