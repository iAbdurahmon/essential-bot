import os
import logging

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from google.cloud import translate

from keyboards.reply import *
from lg_messages.func import lg_check, lg_checker2
from utils.states import Translate, Func1
from data_small import *
from config_reader import config

router = Router()
logger = logging.getLogger(__name__)

if config.google_credentials:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config.google_credentials


def translate_client():
    if not hasattr(translate_client, 'client'):
        translate_client.client = translate.TranslationServiceClient()
    return translate_client.client


@router.message(Func1.choose_option, F.text.in_(trans_btn_all))
async def translator_lg_from(message: Message, state: FSMContext):
    from_lg_checker = lg_check("From: ", "С: ", "dan", message)
    lgs_text = lg_check(languages_en, languages_ru, languages_uz, message)
    detect_text = [lg_check("🪄 Detect language", "🪄 Определить язык", "🪄 Tilni aniqlash", message)]
    backs_text = lg_check("🔙 Back", "🔙 Назад", "🔙 Orqaga", message)
    lgs_text2 = []
    if lg_checker2(message.from_user.id) == 'uz':
        for i in lgs_text:
            lgs_text2.append(f"{i}{from_lg_checker}")
    else:
        for i in lgs_text:
            lgs_text2.append(f"{from_lg_checker}{i}")
    kb_text = detect_text + lgs_text2
    kb_text.append(backs_text)

    kb = (custom_1_3_2(kb_text))

    await message.answer(lg_check("What language do you want to translate from?",
                                  "С какого языка хотите перевести?",
                                  "Qaysi tildan tarjima qilmoqchisiz?", message),
                         reply_markup=kb)
    await state.set_state(Translate.from_lg)


@router.message(Translate.from_lg, F.text.in_(translate_text_all_from))
async def translator_lg_to(message: Message, state: FSMContext):
    to_lg_checker = lg_check("To: ", "На: ", "ga", message)
    lgs_text = lg_check(languages_en, languages_ru, languages_uz, message)
    lgs_text2 = []
    if lg_checker2(message.from_user.id) == 'uz':
        for i in lgs_text:
            lgs_text2.append(f"{i}{to_lg_checker}")
    else:
        for i in lgs_text:
            lgs_text2.append(f"{to_lg_checker}{i}")

    kb = custom_5(lgs_text2 + [lg_check("🏠 Main Menu", "🏠 Главное Меню", "🏠 Asosiy Menyu", message)])
    kb.input_field_placeholder = lg_check(
        'Choose language',
        'Выберите язык',
        'Tilni tanlang', message)

    await message.answer(lg_check("What language do you want to translate to?",
                                  "На какой язык хотите перевести?",
                                  "Qaysi tilga tarjima qilmoqchisiz?", message),
                         reply_markup=kb)
    await state.set_state(Translate.to_lg)
    await state.update_data({'from_lg': message.text})


@router.message(Translate.to_lg, F.text.in_(languages_all_to))
async def translate_text(message: Message, state: FSMContext):
    await message.answer(lg_check("<b>Enter the text you want to translate</b>\n"
                                  "Enter /stop command for exit translate mode",
                                  "<b>Введите текст который хотите перевести</b>\n"
                                  "Введите команду /stop для выхода из режима перевода.",
                                  "<b>Tarjima qilmoqchi bo'lgan matnni kiriting</b>\n"
                                  "Tarjima rejimidan chiqish uchun /stop buyrug'ini kiriting", message),
                         reply_markup=ReplyKeyboardRemove(), parse_mode='html')
    await state.set_state(Translate.text)
    await state.update_data({'to_lg': message.text})


@router.message(Translate.text, F.text)
async def translator_func(message: Message, state: FSMContext):
    data = await state.get_data()
    # None for the "Detect language" button: the API then detects the source itself
    from_lg = lg_db_from.get(data.get('from_lg'))
    to_lg = lg_db_to.get(data.get('to_lg'))

    if not config.google_project:
        await message.answer(lg_check("🛠️ The translator is not configured on this instance.",
                                      "🛠️ Переводчик не настроен на этом сервере.",
                                      "🛠️ Tarjimon bu serverda sozlanmagan.", message))
        return

    try:
        response = translate_client().translate_text(
            contents=[message.text],
            source_language_code=from_lg,
            target_language_code=to_lg,
            parent=f"projects/{config.google_project}"
        )
    except Exception as e:
        logger.exception('translate failed: %s -> %s', from_lg, to_lg)
        await message.answer(lg_check("❌ Could not translate, try again later.",
                                      "❌ Не удалось перевести, попробуйте позже.",
                                      "❌ Tarjima qilolmadim, keyinroq urinib ko'ring.", message))
        return

    await message.answer(f"<b>{response.translations[0].translated_text}</b>")
