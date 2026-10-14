from config_reader import config

admins = [config.admin_id]
group = config.admin_group
invite_coin = 30

languages_en = ['🇬🇧 English', '🇷🇺 Russian', '🇺🇿 Uzbek']
languages_ru = ['🇬🇧 Английский', '🇷🇺 Русский', '🇺🇿 Узбекский']
languages_uz = ["🇬🇧 Inglizcha", "🇷🇺 Ruscha", "🇺🇿 O'zbekcha"]
languages_all = languages_en + languages_ru + languages_uz

languages_en_from = ['From: 🇬🇧 English', 'From: 🇷🇺 Russian', 'From: 🇺🇿 Uzbek']
languages_ru_from = ['С: 🇬🇧 Английский', 'С: 🇷🇺 Русский', 'С: 🇺🇿 Узбекский']
languages_uz_from = ["🇬🇧 Inglizchadan", "🇷🇺 Ruschadan", "🇺🇿 O'zbekchadan"]
languages_all_from = languages_en_from + languages_ru_from + languages_uz_from

languages_en_to = ['To: 🇬🇧 English', 'To: 🇷🇺 Russian', 'To: 🇺🇿 Uzbek']
languages_ru_to = ['На: 🇬🇧 Английский', 'На: 🇷🇺 Русский', 'На: 🇺🇿 Узбекский']
languages_uz_to = ["🇬🇧 Inglizchaga", "🇷🇺 Ruschaga", "🇺🇿 O'zbekchaga"]
languages_all_to = languages_en_to + languages_ru_to + languages_uz_to

detect_lg_text = ["🪄 Detect language", "🪄 Определить язык", "🪄 Tilni aniqlash"]

en_btn_all = [languages_all[i] for i in range(0, len(languages_all), 3)]
ru_btn_all = [languages_all[i + 1] for i in range(0, len(languages_all), 3)]
uz_btn_all = [languages_all[i + 2] for i in range(0, len(languages_all), 3)]

translate_text_all = languages_all + detect_lg_text
translate_text_all_from = languages_all_from + detect_lg_text

lg_db = {'🇬🇧 English': 'en', '🇷🇺 Russian': 'ru', '🇺🇿 Uzbek': 'uz',
         '🇬🇧 Английский': 'en', '🇷🇺 Русский': 'ru', '🇺🇿 Узбекский': 'uz',
         "🇬🇧 Inglizcha": 'en', "🇷🇺 Ruscha": 'ru', "🇺🇿 O'zbekcha": 'uz'}
lg_db_from = {'From: 🇬🇧 English': 'en', 'From: 🇷🇺 Russian': 'ru', 'From: 🇺🇿 Uzbek': 'uz',
              'C: 🇬🇧 Английский': 'en', 'C: 🇷🇺 Русский': 'ru', 'C: 🇺🇿 Узбекский': 'uz',
              "🇬🇧 Inglizchadan": 'en', "🇷🇺 Ruschadan": 'ru', "🇺🇿 O'zbekchadan": 'uz'}
lg_db_to = {'To: 🇬🇧 English': 'en', 'To: 🇷🇺 Russian': 'ru', 'To: 🇺🇿 Uzbek': 'uz',
              'На: 🇬🇧 Английский': 'en', 'На: 🇷🇺 Русский': 'ru', 'На: 🇺🇿 Узбекский': 'uz',
              "🇬🇧 Inglizchaga": 'en', "🇷🇺 Ruschaga": 'ru', "🇺🇿 O'zbekchaga": 'uz'}
# redo
lg_keys = {'ru': '🇷🇺 Русский', 'en': '🇬🇧 English', 'uz': "🇺🇿 O'zbekcha"}

btn_en = ['📝 Quiz-Test', '📚 Word list and books', '💬 Translator', '👤 Profile']
btn_ru = ['📝 Тест-Викторина', '📚 Список слов и книги', '💬 Переводчик', '👤 Профиль']
btn_uz = ["📝 Viktorina Testi", "📚 So'zlar ro'yxati va kitoblar", '💬 Tarjimon', '👤 Profil']
btn_all = btn_uz + btn_ru + btn_en
quiz_btn_all = [btn_all[i] for i in range(0, len(btn_all), 4)]
book_btn_all = [btn_all[i + 1] for i in range(0, len(btn_all), 4)]
trans_btn_all = [btn_all[i + 2] for i in range(0, len(btn_all), 4)]
profile_btn_all = [btn_all[i + 3] for i in range(0, len(btn_all), 4)]

btn_b_l_en = ['📖 Book', "📋 List", "🔙 Back"]
btn_b_l_ru = ['📖 Книга', "📋 Список", "🔙 Назад"]
btn_b_l_uz = ['📖 Kitob', "📋 Ro'yxat", "🔙 Orqaga"]
btn_b_l_all = btn_b_l_uz + btn_b_l_ru + btn_b_l_en
btn_b_l_book = ['📖 Book', '📖 Книга', '📖 Kitob']
btn_b_l_list = ['📋 List', '📋 Список', "📋 Ro'yxat"]

book_names_en = ['📖 Book 1', '📖 Book 2', '📖 Book 3',
                 '📖 Book 4', '📖 Book 5', '📖 Book 6',
                 '🔙 Back', '🏠 Main Menu']
book_names_ru = ['📖 Книга 1', '📖 Книга 2', '📖 Книга 3',
                 '📖 Книга 4', '📖 Книга 5', '📖 Книга 6', '🔙 Назад', '🏠 Главное Меню']
book_names_uz = ['📖 Kitob 1', '📖 Kitob 2', '📖 Kitob 3',
                 '📖 Kitob 4', '📖 Kitob 5', '📖 Kitob 6', '🔙 Orqaga', '🏠 Asosiy Menyu']
book_names_all = book_names_uz + book_names_ru + book_names_en

# Whole books are sent by file_id: Telegram only accepts an id that was uploaded by
# this same bot, so these are filled in per deployment. Send the file to the admin
# group and the bot replies with the id to paste here.
book_ids_en = {}
book_ids_ru = {}
book_ids_uz = {}


# for user
back_menu_en = ['🔙 Back', '🏠 Main Menu']
back_menu_ru = ['🔙 Назад', '🏠 Главное Меню']
back_menu_uz = ['🔙 Orqaga', '🏠 Asosiy Menyu']

# for filter
backs = ['🔙 Back', '🔙 Назад', '🔙 Orqaga']
main_menu = ['🏠 Main Menu', '🏠 Главное Меню', '🏠 Asosiy Menyu']

buttons_data = [("Unit " + str(i), str(i)) for i in range(1, 31)]

lg_reductions = {
    'en': 'eng',
    'ru': 'rus',
    'uz': 'uzb'
}

ready_text_en = 'If everything is ready, click the <b>"Start"</b> button.'
ready_text_ru = 'Если всё готово, нажмите кнопку <b>«Начать»</b>.'
ready_text_uz = """Agar hamma narsa tayyor bo'lsa, <b>«Boshlash»</b> tugmasini bosing."""

profile_buttons_en = ["ℹ️ Bot Version", "🌐 Change Language", "📈 My Rating", "🔗 My Invite Link", "🔙 Back"]
profile_buttons_ru = ["ℹ️ Версия Бота", "🌐 Изменить Язык", "📈 Мой Рейтинг", "🔗 Моя Пригласительная Ссылка", "🔙 Назад"]
profile_buttons_uz = ["ℹ️ Bot Versiyasi", "🌐 Tilni O'zgartirish", "📈 Mening Reytingim", "🔗 Mening Taklif Havolam", "🔙 Orqaga"]
profile_buttons_all = profile_buttons_en + profile_buttons_ru + profile_buttons_uz

version_btn_all = [profile_buttons_all[i] for i in range(0, len(profile_buttons_all), 5)]
lang_change_btn_all = [profile_buttons_all[i + 1] for i in range(0, len(profile_buttons_all), 5)]
rating_btn_all = [profile_buttons_all[i + 2] for i in range(0, len(profile_buttons_all), 5)]
invite_btn_all = [profile_buttons_all[i + 3] for i in range(0, len(profile_buttons_all), 5)]

user_data = {}
