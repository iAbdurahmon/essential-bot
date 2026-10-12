import operator

from aiogram.filters.state import StatesGroup, State
from aiogram.types import CallbackQuery

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Multiselect, Group, Button, Row, Toggle
from aiogram_dialog.widgets.text import Format

from lg_messages.func import lg_check3, lg_checker2
from data_small import *
from dialogs.dialog import russian_not_ready
from utils.states import *
from keyboards.reply import buttons3_custom_no_message


class Poll_manager(StatesGroup):
    unit_select = State()


async def get_data(**kwargs):
    user_info = kwargs.get('event_from_user')
    send_message = lg_check3('📝 Start Quiz-Test', "📝 Начать Тест-Викторину",
                                   "📝 Viktorina testini boshlash", user_info)
    send_all_message = lg_check3('📊 With algorithm', '📊 С алгоритмом', "📊 Algoritm bilan",
                                       user_info)
    book_message = lg_check3('📖 Book', '📖 Книга', "📖 Kitob", user_info)

    lg_en = lg_check3('🇬🇧 English', '🇬🇧 Английский', '🇬🇧 Inglizcha', user_info)
    lg_ru = lg_check3('🇷🇺 Russian', '🇷🇺 Русский', '🇷🇺 Ruscha', user_info)
    lg_uz = lg_check3('🇺🇿 Uzbek', '🇺🇿 Узбекский', "🇺🇿 O'zbekcha", user_info)

    from_text = lg_check3("From", "С", 'dan', user_info)
    to_text = lg_check3("To", "На", "ga", user_info)

    # Uzbek puts the case suffix after the language name, the other two before it
    if lg_checker2(user_info.id) == 'uz':
        toggle_lang_from = [(f'{lg_en}{from_text}', 'en'), (f'{lg_ru}{from_text}', 'ru'),
                            (f'{lg_uz}{from_text}', 'uz')]
        toggle_lang_to = [(f'{lg_uz}{to_text}', 'uz'), (f'{lg_en}{to_text}', 'en'),
                          (f'{lg_ru}{to_text}', 'ru')]
    else:
        toggle_lang_from = [(f'{from_text}: {lg_en}', 'en'), (f'{from_text}: {lg_ru}', 'ru'),
                            (f'{from_text}: {lg_uz}', 'uz')]
        toggle_lang_to = [(f'{to_text}: {lg_uz}', 'uz'), (f'{to_text}: {lg_en}', 'en'),
                          (f'{to_text}: {lg_ru}', 'ru')]

    return {"buttons_data": buttons_data,
            "lg": send_message,
            'lg_all': send_all_message,
            "book_name": book_message,
            "lang_check_from": toggle_lang_from,
            "lang_check_to": toggle_lang_to
            }


async def algorithm(callback: CallbackQuery, button: Button,
                    dialog_manager: DialogManager):
    await callback.answer(lg_check3(
        "🛠️ A Quiz-Test with an algorithm that will help you quickly learn words is under development.\nSoon...",
        "🛠️ Квест-Тест с алгоритмом который поможет быстро выучить слова находится в стадии разработки.\nСкоро...",
        "🛠️ So'zlarni tezda o'rganishga yordam beradigan algoritmga ega Quiz-Test ishlab chiqilmoqda.\nTez orada...",
        callback.from_user
    ), show_alert=True)


async def start_poll(callback: CallbackQuery, button: Button,
                     dialog_manager: DialogManager):
    units = dialog_manager.find('units_poll').get_checked()
    if not units:
        unit_error = lg_check3("❌ Please select at least one unit!",
                                     "❌ Пожалуйста, выберите хотя бы один unit",
                                     "❌ Iltimos, kamida bitta unit'ni tanlang",
                                     callback.from_user)
        await callback.answer(unit_error, show_alert=True)
        return

    lang = lg_checker2(callback.from_user.id)
    checked_from = dialog_manager.find('toogle_lang_from').get_checked() or 'en'
    checked_to = dialog_manager.find('toogle_lang_to').get_checked()
    if not checked_to:
        checked_to = lang if lang != 'en' else 'uz'

    if checked_from == checked_to:
        text = lg_check3("You can't use the same language on both sides!",
                               'Нельзя использовать один и тот же язык с двух сторон!',
                               "Bir xil tilni ikki tomonda ishlatib bo'lmaydi!", callback.from_user)
        await callback.answer(text, show_alert=True)
        return

    # the word tables are English-centred: ru <-> uz pairs have no data behind them
    if 'en' not in (checked_from, checked_to):
        text = lg_check3("One of the two languages has to be English!",
                               'Один из двух языков должен быть английским!',
                               "Ikki tildan biri ingliz tili bo'lishi kerak!", callback.from_user)
        await callback.answer(text, show_alert=True)
        return

    book = dialog_manager.start_data['book']
    if 'ru' in (checked_from, checked_to) and await russian_not_ready(callback, book, 'ru'):
        return

    units_int = [int(i) for i in units]
    user_data[callback.from_user.id] = {'from': checked_from, 'to': checked_to,
                                        'book': book, 'units': units_int}

    unit_selected_text = ', '.join(str(i) for i in units_int)
    languages_text = f"{lg_keys.get(checked_from)} ➡ {lg_keys.get(checked_to)}"

    en_pretext = (f"📕 Selected book: {book}\n"
                  f"🖇️ Selected units: {unit_selected_text}\n"
                  f"🌐 Selected languages: {languages_text}\n\n{ready_text_en}")
    ru_pretext = (f"📕 Выбранная книга: {book}\n"
                  f"🖇️ Выбранные unit: {unit_selected_text}\n"
                  f"🌐 Выбранные языки: {languages_text}\n\n{ready_text_ru}")
    uz_pretext = (f"📕 Tanlangan  kitob: {book}\n"
                  f"🖇️ Tanlangan unitlar: {unit_selected_text}\n"
                  f"🌐 Tanlangan tillar: {languages_text}\n\n{ready_text_uz}")

    await callback.message.answer(lg_check3(en_pretext, ru_pretext, uz_pretext, callback.from_user),
                                  reply_markup=buttons3_custom_no_message(
                                      [lg_check3('🏁 Start',
                                                 '🏁 Начать',
                                                 '🏁 Boshlash',
                                                 callback.from_user),
                                       lg_check3('🔙 Back', '🔙 Назад', '🔙 Orqaga', callback.from_user),
                                       lg_check3('🏠 Main Menu', '🏠 Главное Меню', '🏠 Asosiy Menyu', callback.from_user)
                                       ]))

    await dialog_manager.done()


dialog = Dialog(
    Window(
        Format('{book_name} {start_data[book]}:'),
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
