import operator

from aiogram import Router, F
from aiogram.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.scene import SceneRegistry
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.widgets.kbd import Multiselect, Group, Button, Row, Radio, Toggle
from aiogram_dialog.widgets.text import Format

from lg_messages.func import lg_check2, lg_checker2, lg_check, lg_check3
from data_small import *
from dialogs.main_poll import QuizScene, router_poll
from utils.states import *
from keyboards.reply import buttons3_custom_no_message

router = Router()


class Poll_manager(StatesGroup):
    unit_select = State()


async def get_data(**kwargs):
    user_info = kwargs.get('event_from_user')
    send_message = await lg_check2('📝 Start Quiz-Test', "📝 Начать Тест-Викторину",
                                   "📝 Viktorina testini boshlash", user_info)
    send_all_message = await lg_check2('📊 With algorithm', '📊 С алгоритмом', "📊 Algoritm bilan",
                                       user_info)
    book_message = await lg_check2('📖 Book', '📖 Книга', "📖 Kitob", user_info)

    lg_en = await lg_check2('🇬🇧 English', '🇬🇧 Английский', '🇬🇧 Inglizcha', user_info)
    lg_ru = await lg_check2('🇷🇺 Russian', '🇷🇺 Русский', '🇷🇺 Ruscha', user_info)
    lg_uz = await lg_check2('🇺🇿 Uzbek', '🇺🇿 Узбекский', "🇺🇿 O'zbekcha", user_info)

    from_text = await lg_check2("From", "С", 'dan', user_info)
    to_text = await lg_check2("To", "На", "ga", user_info)

    toggle_lang_from = None
    toggle_lang_to = None

    lang_user = lg_checker2(user_info.id)

    if lang_user == 'uz':
        toggle_lang_from = [(f'{lg_en}{from_text}', 'en'), (f'{lg_ru}{from_text}', 'ru'), (f'{lg_uz}{from_text}', 'uz')]
        toggle_lang_to = [(f'{lg_uz}{to_text}', 'uz'), (f'{lg_en}{to_text}', 'en'), (f'{lg_ru}{to_text}', 'ru')]
    elif lang_user == 'en':
        toggle_lang_from = [(f'{from_text}: {lg_en}', 'en'), (f'{from_text}: {lg_ru}', 'ru'),
                            (f'{from_text}: {lg_uz}', 'uz')]
        toggle_lang_to = [(f'{to_text}: {lg_uz}', 'uz'), (f'{to_text}: {lg_en}', 'en'), (f'{to_text}: {lg_ru}', 'ru')]
    elif lang_user == 'ru':
        toggle_lang_from = [(f'{from_text}: {lg_en}', 'en'), (f'{from_text}: {lg_ru}', 'ru'),
                            (f'{from_text}: {lg_uz}', 'uz')]
        toggle_lang_to = [(f'{to_text}: {lg_ru}', 'ru'), (f'{to_text}: {lg_uz}', 'uz'), (f'{to_text}: {lg_en}', 'en'), ]

    return {"buttons_data": buttons_data,
            "lg": send_message,
            'lg_all': send_all_message,
            "book_name": book_message,
            "lang_check_from": toggle_lang_from,
            "lang_check_to": toggle_lang_to
            }


async def algorithm(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    await callback.answer(await lg_check2(
        "🛠️ A Quiz-Test with an algorithm that will help you quickly learn words is under development.\nSoon...",
        "🛠️ Квест-Тест с алгоритмом который поможет быстро выучить слова находится в стадии разработки.\nСкоро...",
        "🛠️ So'zlarni tezda o'rganishga yordam beradigan algoritmga ega Quiz-Test ishlab chiqilmoqda.\nTez orada...",
        callback.from_user
    ), show_alert=True)


async def start_poll(callback: CallbackQuery, button: Button,
                     dialog_manager: DialogManager):
    widget1 = dialog_manager.find('toogle_lang_from')
    widget2 = dialog_manager.find('toogle_lang_to')
    checked_from = widget1.get_checked()
    checked_to = widget2.get_checked()
    lang = lg_checker2(callback.from_user.id)

    unit_widget = dialog_manager.find('units_poll')
    units = unit_widget.get_checked()
    units_int = [int(i) for i in units]

    if not units:
        unit_error = await lg_check2("❌ Please select at least one unit!",
                                     "❌ Пожалуйста, выберите хотя бы один unit",
                                     "❌ Iltimos, kamida bitta unit'ni tanlang",
                                     callback.from_user)
        await callback.answer(unit_error, show_alert=True)
        return

    if not checked_to and not checked_from:
        if lang == 'en':
            checked_from = 'en'
            checked_to = 'uz'
        else:
            checked_from = 'en'
            checked_to = lang
    else:
        pass
    if not checked_from:
        checked_from = 'en'
    if not checked_to:
        if lang != 'ru':
            checked_to = 'uz'
        else:
            checked_to = lang

    if checked_from == 'en':
        if checked_to == 'en':
            text = await lg_check2("You can't use English languages together at the same time!",
                                   'Нельзя использовать английские языкы вместе одновременно!',
                                   "Ingliz tillarni bir vaqtda birga ishlatib bo'lmaydi!", callback.from_user)
            await callback.answer(text, show_alert=True)
            return
    elif checked_from == 'ru':
        if checked_to == 'uz':
            text = await lg_check2("You can't use Russian language together with Uzbek at the same time!",
                                   "Нельзя использовать русский язык вместе с узбекским одновременно!",
                                   "Rus va o'zbek tillarni bir vaqtda birga ishlatib bo'lmaydi!", callback.from_user)
            await callback.answer(text, show_alert=True)
            return
        if checked_to == 'ru':
            text = await lg_check2("You can't use Russian languages together at the same time!",
                                   'Нельзя использовать русские языки вместе одновременно!',
                                   "Rus tillarni bir vaqtda birga ishlatib bo'lmaydi!", callback.from_user)
            await callback.answer(text, show_alert=True)
            return
    elif checked_from == 'uz':
        if checked_to == 'ru':
            text = await lg_check2("You can't use Uzbek language together with Russian at the same time!",
                                   'Нельзя использовать узбекский язык вместе с русским одновременно!',
                                   "O'zbek va rus tillarni bir vaqtda ishlatib bo'lmaydi!", callback.from_user)
            await callback.answer(text, show_alert=True)
            return
        if checked_to == 'uz':
            text = await lg_check2("You can't use Uzbek languages together at the same timee!",
                                   'Нельзя использовать узбекские языки вместе одновременно!',
                                   "O'zbek tillarni bir vaqtda birga ishlatib bo'lmaydi!", callback.from_user)
            await callback.answer(text, show_alert=True)
            return
    # data_for_lg['from'] = checked_from
    # data_for_lg['to'] = checked_to
    #
    # for i in units_int:
    #     unit_selected.append(i)
    #
    # book_selected.append(dialog_manager.start_data[0])

    book = dialog_manager.start_data[0]

    if not (book == '1' or book == '2') and (checked_from == 'ru' or checked_to == 'ru'):
        text = await lg_check2("Since we do the Russian translation manually, at the moment only operations from the first book work.\n"
                               "Follow the news on the channel: @essentialwordchannel",
                               'Так как русский перевод мы делаем вручную, на данный момент только работают операции с первой книги.\n'
                               'Следите за новостями на канале: @essentialwordchannel',
                               "Rus tiliga tarjimani o'zimiz qilganimiz uchun, hozircha faqat birinchi kitob bilan ishlashingiz mumkin.\n"
                               "Yangiliklarni kanalda kuzating: @essentialwordchannel", callback.from_user)
        await callback.answer(text, show_alert=True)
        return

    wrem_list = []
    for i in units_int:
        wrem_list.append(i)
        user_data[callback.from_user.id] = {'from': checked_from, 'to': checked_to,
                                            'book': book, 'units': wrem_list}

    unit_selected_text_comma = ''
    data = user_data.get(callback.from_user.id)
    unit_selected = data.get('units')
    for i in unit_selected:
        unit_selected_text_comma += f"{i}, "
    unit_selected_text = unit_selected_text_comma.rstrip(', ')

    en_pretext = (f"📕 Selected book: {book}\n"
                  f"🖇️ Selected units: {unit_selected_text}\n"
                  f"🌐 Selected languages: {lg_keys.get(checked_from)} ➡ {lg_keys.get(checked_to)}\n\n{ready_text_en}")
    ru_pretext = (f"📕 Выбранная книга: {book}\n"
                  f"🖇️ Выбранные unit: {unit_selected_text}\n"
                  f"🌐 Выбранные языки: {lg_keys.get(checked_from)} ➡ {lg_keys.get(checked_to)}\n\n{ready_text_ru}")
    uz_pretext = (f"📕 Tanlangan  kitob: {book}\n"
                  f"🖇️ Tanlangan unitlar: {unit_selected_text}\n"
                  f"🌐 Tanlangan tillar: {lg_keys.get(checked_from)} ➡ {lg_keys.get(checked_to)}\n\n{ready_text_uz}")

    await callback.message.answer(lg_check3(en_pretext, ru_pretext, uz_pretext, callback.from_user),
                                  reply_markup=buttons3_custom_no_message(
                                      [lg_check3('🏁 Start',
                                                 '🏁 Начать',
                                                 '🏁 Boshlash',
                                                 callback.from_user),
                                       lg_check3('🔙 Back', '🔙 Назад', '🔙 Orqaga', callback.from_user),
                                       lg_check3('🏠 Main Menu', '🏠 Главное Меню', '🏠 Asosiy Menyu', callback.from_user)
                                       ]))

    router_poll.message.register(QuizScene.as_handler(), Poll_state.dialog_started)

    await dialog_manager.done()


dialog = Dialog(
    Window(
        Format('{book_name} {start_data[0]}:'),
        Row(
            Toggle(
                Format('{item[0]}'),
                id='toogle_lang_from',
                item_id_getter=operator.itemgetter(1),
                items='lang_check_from',
            ),
            Toggle(
                Format('{item[0]}'),
                id='toogle_lang_to',
                item_id_getter=operator.itemgetter(1),
                items='lang_check_to',
            )
        ),
        Group(
            Multiselect(
                Format("✅ {item[0]}"),
                Format("{item[0]}"),
                id='units_poll',
                item_id_getter=operator.itemgetter(1),
                items="buttons_data"
            ),
            width=3
        ),
        Row(
            Button(
                Format("{lg_all}"), id='send_all', on_click=algorithm
            ),
            Button(
                Format("{lg}"), id='ok', on_click=start_poll
            )
        ),
        state=Poll_manager.unit_select,
        getter=get_data
    )
)
