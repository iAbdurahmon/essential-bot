from tests.conftest import TEST_USER_ID
from tests.mocked import make_user, message_update
from tools.db_conn import fetch_one


async def test_start_asks_for_language_when_user_is_unknown(dp, bot, session):
    user = make_user(TEST_USER_ID)
    await dp.feed_update(bot, message_update(user, '/start'))

    texts = session.sent_texts()
    assert any('Hello' in t for t in texts), texts
    assert 'Choose language' in texts[-1]


async def test_choosing_a_language_creates_the_user(dp, bot, session):
    user = make_user(TEST_USER_ID)
    await dp.feed_update(bot, message_update(user, '/start'))
    session.clear()

    await dp.feed_update(bot, message_update(user, '🇷🇺 Russian', update_id=2))

    row = fetch_one('SELECT tg_id, lg, status FROM users WHERE tg_id = %s', (TEST_USER_ID,))
    assert row == (TEST_USER_ID, 'ru', 1)
    # the confirmation has to come in the language that was just picked
    assert any('успешно выбрали язык' in t for t in session.sent_texts()), session.sent_texts()


async def test_start_shows_the_menu_to_a_known_user(dp, bot, session, db_user):
    db_user(lg='uz')
    await dp.feed_update(bot, message_update(make_user(TEST_USER_ID), '/start'))

    assert any('Variantni tanlang' in t for t in session.sent_texts()), session.sent_texts()


async def test_balance_reports_the_stored_rank(dp, bot, session, db_user):
    db_user(lg='en', rank=137)
    await dp.feed_update(bot, message_update(make_user(TEST_USER_ID), '/balance'))

    assert '137 coin' in session.sent_texts()[-1]


async def test_balance_does_not_crash_for_an_unknown_user(dp, bot, session):
    await dp.feed_update(bot, message_update(make_user(TEST_USER_ID), '/balance'))

    assert '0 coin' in session.sent_texts()[-1]


async def test_statistics_counts_users(dp, bot, session, db_user):
    db_user(lg='en')
    await dp.feed_update(bot, message_update(make_user(TEST_USER_ID), '/statistics'))

    text = session.sent_texts()[-1]
    assert 'Statistic' in text and 'Total users' in text


async def test_top10_marks_the_requesting_user(dp, bot, session, db_user):
    db_user(lg='en', rank=5, name='Tester')
    await dp.feed_update(bot, message_update(make_user(TEST_USER_ID), '/top10'))

    text = session.sent_texts()[0]
    assert 'TOP 10' in text
    assert '(You)' in text, text


async def test_language_falls_back_instead_of_greeting(dp, bot, session, db_user):
    # lg_check used to return a greeting when the language was unknown, so a button
    # label could come out as "Hello, Tester!"
    db_user(lg=None)
    await dp.feed_update(bot, message_update(make_user(TEST_USER_ID, lg='fr'), '/balance'))

    assert 'Your balance' in session.sent_texts()[-1]
