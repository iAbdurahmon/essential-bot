import os
from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

from easygoogletranslate import EasyGoogleTranslate
from google.cloud import translate

from keyboards.reply import *
from lg_messages.func import lg_check, lg_checker2
from utils.states import Translate, Func1
from data_small import *
from tools.db_conn import cur, conn

router = Router()
translator = EasyGoogleTranslate()


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
async def translator_func(message: Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    from_lg = data.get('from_lg')
    to_lg = data.get('to_lg')
    text = message.text
    from_lg = lg_db_from.get(from_lg)
    to_lg = lg_db_to.get(to_lg)

    def detect_checker(from_lg_arg):
        if from_lg_arg in detect_lg_text:
            return None
        else:
            return from_lg

    def translate_text_func(credentials_path, text, source_language, target_language):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        client = translate.TranslationServiceClient()
        parent = f"projects/abdurahmon"
        response = client.translate_text(
            contents=[text],
            source_language_code=source_language,
            target_language_code=target_language,
            parent=parent
        )
        return response.translations[0].translated_text
    credentials_path = 'abdurahmon-dfc180ec4c48.json'
    text_to_translate = text
    source_language = detect_checker(from_lg)
    target_language = to_lg
    result = translate_text_func(credentials_path, text_to_translate, source_language, target_language)

    await message.answer(f"<b>{result}</b>")
    await bot.send_message(group, f"#translator\n"
                                  f"{result}\n"
                                  f"{message.from_user.first_name}\n"
                           f"@{message.from_user.username}\n"
                           f"{message.from_user.id}")
