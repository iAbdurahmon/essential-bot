from aiogram.fsm.storage.base import StorageKey

from tests.conftest import TEST_USER_ID
from tests.mocked import callback_update, make_user, message_update
from tools.db_conn import fetch_all
from utils.states import Func1, WordList


async def set_state(dp, bot, user, state):
    await dp.storage.set_state(StorageKey(bot_id=bot.id, chat_id=user.id, user_id=user.id), state)


async def test_word_list_walks_from_book_to_unit(dp, bot, session, db_user):
    db_user(lg='ru')
    user = make_user(TEST_USER_ID)
    await set_state(dp, bot, user, Func1.choose_book_or_list)

    await dp.feed_update(bot, message_update(user, '📋 Список'))
    assert 'Выберите книгу' in session.sent_texts()[-1]

    session.clear()
    await dp.feed_update(bot, message_update(user, '📖 Книга 1', update_id=2))
    text = session.sent_texts()[-1]
    assert 'Книга 1' in text and 'Выберите unit' in text

    # 30 unit buttons plus the back row
    keyboard = session.calls[-1].reply_markup.inline_keyboard
    assert sum(len(row) for row in keyboard) == 31
    assert keyboard[-1][0].callback_data == 'wl:back'


async def test_word_list_prints_the_words_of_a_unit(dp, bot, session, db_user):
    db_user(lg='ru')
    user = make_user(TEST_USER_ID)
    await set_state(dp, bot, user, WordList.choose_unit)

    await dp.feed_update(bot, callback_update(user, 'wl:1:1', update_id=3))

    text = '\n'.join(session.sent_texts())
    assert 'Книга 1, Unit 1' in text

    # every word of the unit has to be listed, numbered, English against the user's
    # language; asserting on a word count would tie the test to how much data is loaded
    rows = fetch_all('SELECT eng, rus FROM book1 WHERE unit = 1 ORDER BY id')
    assert rows, 'book1 unit 1 has no words, is the seed applied?'
    for num, (word, meaning) in enumerate(rows, 1):
        assert f'<b>{num}.</b> {word} — {meaning}' in text, f'missing word {num}: {word}'


async def test_word_list_answers_an_empty_unit_without_crashing(dp, bot, session, db_user):
    db_user(lg='en')
    user = make_user(TEST_USER_ID)
    await set_state(dp, bot, user, WordList.choose_unit)

    await dp.feed_update(bot, callback_update(user, 'wl:1:99', update_id=4))

    assert not session.sent_texts()
    answers = [c for c in session.calls if type(c).__name__ == 'AnswerCallbackQuery']
    assert answers and 'no words' in answers[-1].text.lower()
