import operator
import asyncio
import os
import time

from contextlib import suppress
from typing import Any

from aiogram import Router
from aiogram.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, ContentType
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.chat_action import ChatActionSender

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Multiselect, Group, Button, Row, Radio
from aiogram_dialog.widgets.text import Format, Multi, Progress
from aiogram_dialog.widgets.media import StaticMedia

from lg_messages.func import lg_check2, lg_check3
from tools.pdf import pdf_setup, pdf_namer
from data_small import *
from keyboards.reply import func_kb2

router = Router()


class Unit(StatesGroup):
    unit_state = State()
    load = State()
    send_file = State()


async def get_data(**kwargs):
    user_info = kwargs.get('event_from_user')
    send_message = await lg_check2('📤 Send the Units', "📤 Отправить Unit",
                                   "📤 Unitlarni jo'natish", user_info)
    send_all_message = await lg_check2('📗 Send the whole book', '📗 Отправить всю книгу', "📗 Butun kitobni yuborish",
                                       user_info)
    book_message = await lg_check2('📖 Book', '📖 Книга', "📖 Kitob", user_info)

    lg_en = await lg_check2('English', 'Английский', 'Inglizcha', user_info)
    lg_ru = await lg_check2('Russian', 'Русский', 'Ruscha', user_info)
    lg_uz = await lg_check2('Uzbek', 'Узбекский', "O'zbekcha", user_info)

    return {"buttons_data": buttons_data,
            "lg": send_message,
            'lg_all': send_all_message,
            "book_name": book_message,
            "lang_check": [(lg_en, 'en'), (lg_ru, 'ru'), (lg_uz, 'uz')]}


async def get_bg_data(dialog_manager: DialogManager, **kwargs):
    user_info = kwargs.get('event_from_user')
    wait_message = await lg_check2('⏳ Preparation...', '⏳ Подготовка...', "⏳ Tayyorlanmoqda...", user_info)
    return {
        "progress": dialog_manager.dialog_data.get("progress", 0),
        "wait_mg": wait_message,
        "user_info": user_info
    }


async def send_getter(dialog_manager: DialogManager, **kwargs):
    units = dialog_manager.start_data.get('units')
    unit_text = ', '.join('#u' + str(unit) for unit in units)
    point_mg = dialog_manager.start_data.get('point')
    point_cm_mg = dialog_manager.start_data.get('point_cm')
    return {
        "data": dialog_manager.start_data,
        "back_mg_get": dialog_manager.start_data,
        "main_mg_get": dialog_manager.start_data,
        "book_mg": dialog_manager.start_data,
        "units_mg": unit_text,
        "book_name_mg": dialog_manager.start_data,
        "point_mg": point_mg,
        "point_cm_mg": point_cm_mg
    }


async def book_sender(callback: CallbackQuery, button: Button,
                      manager: DialogManager):
    widget_lang = manager.find('lang')
    lang = widget_lang.get_checked()
    book_name = manager.start_data[0]
    if not (book_name == '1' or book_name == '2') and lang == 'ru':
        text = await lg_check2(
            "Since we do the Russian translation manually, at the moment only operations from the Book 1 and Book 2 work.\n"
            "Follow the news on the channel: @essentialwordchannel",
            'Так как русский перевод мы делаем вручную, на данный момент только работают операции с первой и второй книги.\n'
            'Следите за новостями на канале: @essentialwordchannel',
            "Rus tiliga tarjimani o'zimiz qilganimiz uchun, hozircha faqat birinchi va ikkinchi kitoblar bilan ishlashingiz mumkin.\n"
            "Yangiliklarni kanalda kuzating: @essentialwordchannel", callback.from_user)
        await callback.answer(text, show_alert=True)
        return
    if lang == 'uz':
        book_id = book_ids_uz.get(int(book_name))
        await callback.message.answer_document(book_id)
        await callback.bot.send_message(group,
                                     f'#fileBook{book_name}\n{callback.from_user.first_name} - @{callback.from_user.username} - {callback.from_user.id}')
    elif lang == 'en':
        book_id = book_ids_en.get(int(book_name))
        await callback.message.answer_document(book_id)
    elif lang == 'ru':
        book_id = book_ids_ru.get(int(book_name))
        await callback.message.answer_document(book_id)


async def ok_button(event: CallbackQuery, button: Button,
                    manager: DialogManager):
    book = manager.start_data[0]
    widget_lang = manager.find('lang')
    lang = widget_lang.get_checked()
    print('button')
    if not (book == '1' or book == '2') and lang == 'ru':
        text = await lg_check2("Since we do the Russian translation manually, at the moment only operations from the Book 1 and Book 2 work.\n"
                               "Follow the news on the channel: @essentialwordchannel",
                               'Так как русский перевод мы делаем вручную, на данный момент только работают операции с первой и второй книги.\n'
                               'Следите за новостями на канале: @essentialwordchannel',
                               "Rus tiliga tarjimani o'zimiz qilganimiz uchun, hozircha faqat birinchi va ikkinchi kitoblar bilan ishlashingiz mumkin.\n"
                               "Yangiliklarni kanalda kuzating: @essentialwordchannel", event.from_user)
        await event.answer(text, show_alert=True)
        return
    widget = manager.find('units')
    checked = widget.get_checked()
    if not checked:
        unit_error = await lg_check2("❌ Please select at least one unit!",
                                     "❌ Пожалуйста, выберите хотя бы один unit",
                                     "❌ Iltimos, kamida bitta unit'ni tanlang",
                                     event.from_user)
        await event.answer(unit_error, show_alert=True)
        return
    await manager.update({'progress': 20})
    await manager.update({'progress': 30})
    await manager.update({'progress': 40})
    await manager.switch_to(Unit.load)
    await manager.update({'progress': 50})
    file_name = pdf_namer(checked, lang)
    await manager.update({'progress': 60})
    await asyncio.create_task(send_func(manager.bg(), checked, book, lang))
    await manager.update({'progress': 70})
    try:
        message_id = text_for_edit['editer']
    except Exception as e:
        await event.answer("Error 404. Try again!", show_alert=True)
        for admin in admins:
            await event.bot.send_message(admin, f"{e} for user: {event.from_user.id}")
        return
    with suppress(TelegramBadRequest):
        await event.bot.delete_message(event.message.chat.id, message_id)
    await manager.update({'progress': 80})
    back_mg = lg_check3('🔙 Back', '🔙 Назад', '🔙 Orqaga', event.from_user)
    await manager.update({'progress': 85})
    main_mg = lg_check3('🏠 Main Menu', '🏠 Главное Меню', '🏠 Asosiy Menyu', event.from_user)
    await manager.update({'progress': 80})
    book_name = lg_check3('Book', 'Книга',  'Kitob', event.from_user)
    await manager.update({'progress': 90})
    data_dict = {'path': file_name,
                 'back_mg': back_mg,
                 'main_mg': main_mg,
                 'book': book,
                 'units': checked,
                 'book_name': book_name}
    await manager.update({'progress': 100})
    send_mg = await event.message.answer(lg_check3('📤 Sending...', '📤 Отправка...', "📤 Jo'natilmoqda...", event.from_user),
                                         reply_markup=func_kb2(
                                             lg_check3(back_menu_en, back_menu_ru, back_menu_uz, event.from_user),
                                             event.from_user)
                                         )
    await manager.done()
    async with ChatActionSender.upload_document(bot=event.bot, chat_id=event.message.chat.id):
        await manager.start(Unit.send_file, data=data_dict)
    send_mg_id = send_mg.message_id
    await event.bot.delete_message(event.message.chat.id, send_mg_id)
    await event.message.answer(lg_check3('🔘 Choose button', '🔘 Выберите кнопку', "🔘 Tugmani bosing", event.from_user),
                               reply_markup=func_kb2(
                                   lg_check3(back_menu_en, back_menu_ru, back_menu_uz, event.from_user),
                                   event.from_user)
                               )
    await event.bot.send_message(group, f'#file\n{event.from_user.first_name} - @{event.from_user.username} - {event.from_user.id}')
    os.remove(file_name)


async def send_func(manager: DialogManager, checked, book, lang):
    pdf_setup(checked, book, lang)


async def on_dialog_start(start_data: Any, dialog_manager: DialogManager):
    widget = dialog_manager.find('lang')
    await widget.set_checked('en')


dialog = Dialog(
    Window(
        Format('{book_name} {start_data[0]}:'),
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
