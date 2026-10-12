from aiogram.fsm.storage.base import StorageKey
from aiogram.types import PollAnswer, Update

from data_small import user_data
from tests.conftest import TEST_USER_ID
from tests.mocked import make_user, message_update
from tools.db_conn import fetch_value
from utils.states import Poll_state


async def enter_quiz(dp, bot, user, units=None):
    # this is the state start_poll leaves behind before the scene takes over
    user_data[user.id] = {'from': 'en', 'to': 'uz', 'book': '1', 'units': units or [1]}
    key = StorageKey(bot_id=bot.id, chat_id=user.id, user_id=user.id)
    await dp.storage.set_state(key, Poll_state.dialog_started)
    await dp.feed_update(bot, message_update(user, '🏁 Start'))


def poll_answer_update(user, option_id, update_id=50):
    return Update(update_id=update_id,
                  poll_answer=PollAnswer(poll_id='poll1', user=user, option_ids=[option_id]))


async def test_quiz_sends_a_well_formed_poll(dp, bot, session, db_user):
    db_user(lg='en')
    await enter_quiz(dp, bot, make_user(TEST_USER_ID))

    polls = session.polls()
    assert len(polls) == 1
    poll = polls[0]
    assert len(poll.options) == 4
    assert len(set(poll.options)) == 4, 'duplicate options would make two identical buttons'
    assert 0 <= poll.correct_option_id < 4
    assert poll.type == 'quiz'
    assert poll.question.startswith('1. ')


async def test_answering_advances_to_the_next_question(dp, bot, session, db_user):
    db_user(lg='en')
    user = make_user(TEST_USER_ID)
    await enter_quiz(dp, bot, user)
    first = session.polls()[0]
    session.clear()

    await dp.feed_update(bot, poll_answer_update(user, first.correct_option_id))

    polls = session.polls()
    assert len(polls) == 1, 'an answer has to be followed by exactly one new poll'
    assert polls[0].question.startswith('2. ')
    assert polls[0].question != first.question


async def test_a_correct_answer_is_scored_and_paid(dp, bot, session, db_user):
    db_user(lg='en', rank=0)
    user = make_user(TEST_USER_ID)
    await enter_quiz(dp, bot, user)
    first = session.polls()[0]

    await dp.feed_update(bot, poll_answer_update(user, first.correct_option_id))
    session.clear()
    await dp.feed_update(bot, message_update(user, '🚫 Stop', update_id=60))

    results = '\n'.join(session.sent_texts())
    assert 'Correct:_ *1*' in results, results
    assert 'Incorrect:_ *0*' in results, results
    # two coins per correct answer, credited to the rating
    assert fetch_value('SELECT rank FROM users WHERE tg_id = %s', (TEST_USER_ID,)) == 2
    assert 'You have earned 2' in results


async def test_a_wrong_answer_is_scored_as_wrong(dp, bot, session, db_user):
    db_user(lg='en', rank=0)
    user = make_user(TEST_USER_ID)
    await enter_quiz(dp, bot, user)
    first = session.polls()[0]
    wrong = (first.correct_option_id + 1) % 4

    await dp.feed_update(bot, poll_answer_update(user, wrong))
    session.clear()
    await dp.feed_update(bot, message_update(user, '🚫 Stop', update_id=60))

    results = '\n'.join(session.sent_texts())
    assert 'Correct:_ *0*' in results, results
    assert 'Incorrect:_ *1*' in results, results
    assert fetch_value('SELECT rank FROM users WHERE tg_id = %s', (TEST_USER_ID,)) == 0


async def test_skipping_counts_the_question_as_missed(dp, bot, session, db_user):
    db_user(lg='en')
    user = make_user(TEST_USER_ID)
    await enter_quiz(dp, bot, user)
    session.clear()

    await dp.feed_update(bot, message_update(user, '➡️ Next', update_id=61))
    assert session.polls()[0].question.startswith('2. ')

    session.clear()
    await dp.feed_update(bot, message_update(user, '🚫 Stop', update_id=62))
    results = '\n'.join(session.sent_texts())
    # the skipped one and the one on screen when Stop was pressed
    assert 'Missed:_ *2*' in results, results
    assert 'Correct:_ *0*' in results, results


async def test_the_answer_is_matched_to_the_question_that_was_asked(dp, bot, session, db_user):
    """The old code reshuffled the question list on every step while the step index
    pointed into the previous order, so an answer could be scored against another
    question. Answer three in a row correctly and all three must count."""
    db_user(lg='en', rank=0)
    user = make_user(TEST_USER_ID)
    await enter_quiz(dp, bot, user, units=[1, 2])

    asked = []
    for step in range(3):
        poll = session.polls()[-1]
        asked.append(poll.question)
        await dp.feed_update(bot, poll_answer_update(user, poll.correct_option_id,
                                                    update_id=70 + step))

    session.clear()
    await dp.feed_update(bot, message_update(user, '🚫 Stop', update_id=80))

    results = '\n'.join(session.sent_texts())
    assert len(set(asked)) == 3, 'the same question was asked twice'
    assert 'Correct:_ *3*' in results, results
    assert fetch_value('SELECT rank FROM users WHERE tg_id = %s', (TEST_USER_ID,)) == 6


async def test_quiz_without_settings_does_not_crash(dp, bot, session, db_user):
    db_user(lg='en')
    user = make_user(TEST_USER_ID)
    user_data.pop(user.id, None)
    key = StorageKey(bot_id=bot.id, chat_id=user.id, user_id=user.id)
    await dp.storage.set_state(key, Poll_state.dialog_started)

    await dp.feed_update(bot, message_update(user, '🏁 Start'))

    assert not session.polls()
    assert 'no words' in session.sent_texts()[-1].lower(), session.sent_texts()


async def test_repeating_a_quiz_with_the_same_result_pays_nothing(dp, bot, session, db_user):
    """Coins are paid for beating the stored result of a unit, not for repeating it."""
    db_user(lg='en', rank=0)
    user = make_user(TEST_USER_ID)

    async def one_correct_answer(base):
        await enter_quiz(dp, bot, user)
        poll = session.polls()[-1]
        await dp.feed_update(bot, poll_answer_update(user, poll.correct_option_id, base))
        await dp.feed_update(bot, message_update(user, '🚫 Stop', update_id=base + 1))
        return fetch_value('SELECT rank FROM users WHERE tg_id = %s', (TEST_USER_ID,))

    first = await one_correct_answer(90)
    assert first == 2, 'the first correct answer has to be paid'

    session.clear()
    second = await one_correct_answer(95)
    assert second == first, 'repeating the same result must not pay twice'


async def test_a_user_without_a_mongo_balance_gets_one(dp, bot, session, db_user):
    from tools.db_conn import collection
    db_user(lg='en')
    assert collection.find_one({'tg_id': TEST_USER_ID}) is None

    await enter_quiz(dp, bot, make_user(TEST_USER_ID))

    doc = collection.find_one({'tg_id': TEST_USER_ID}, {'balance': 1})
    assert doc and len(doc['balance']) == 6, 'six books have to be initialised'
