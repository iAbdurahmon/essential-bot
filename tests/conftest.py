import asyncio

import pytest
import pytest_asyncio

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

import main
from data_small import user_data
from tests.mocked import MockedSession
from tools.db_conn import collection, execute, fetch_one

# ids far outside the Telegram range, so a test can never touch a real account
TEST_USER_ID = 900000001
TEST_INVITER_ID = 900000002


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def session():
    return MockedSession()


@pytest.fixture(scope='session')
def bot(session):
    return Bot(token='42:TEST', session=session,
               default=DefaultBotProperties(parse_mode='HTML'))


@pytest.fixture(scope='session')
def dp():
    # the routers are module-level objects, so only one dispatcher may own them
    return main.dp_setup(MemoryStorage())


def wipe_test_users():
    for user_id in (TEST_USER_ID, TEST_INVITER_ID):
        execute('DELETE FROM users WHERE tg_id = %s', (user_id,))
    # per-unit balances live in Mongo and the coin payout depends on the previous
    # result for that unit, so a leftover document changes what the next test earns
    collection.delete_many({'tg_id': {'$in': [TEST_USER_ID, TEST_INVITER_ID]}})


@pytest_asyncio.fixture(autouse=True)
async def clean_state(session, dp, bot):
    session.clear()
    user_data.clear()
    wipe_test_users()
    yield
    wipe_test_users()
    user_data.clear()
    await dp.storage.close()


@pytest.fixture
def db_user():
    def create(user_id=TEST_USER_ID, lg='en', rank=0, name='Tester'):
        execute('INSERT INTO users (name, username, tg_id, created_on, lg, status, rank) '
                'VALUES (%s, %s, %s, now(), %s, 1, %s)',
                (name, f'tester{user_id}', user_id, lg, rank))
        from lg_messages.func import drop_lang_cache
        drop_lang_cache(user_id)
        return fetch_one('SELECT tg_id, lg, rank FROM users WHERE tg_id = %s', (user_id,))
    return create
