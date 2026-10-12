import datetime
from typing import Any, Optional

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import TelegramMethod
from aiogram.types import CallbackQuery, Chat, Message, Poll, PollOption, Update, User

BOT_ID = 999999
BOT_USER = User(id=BOT_ID, is_bot=True, first_name='TestBot', username='test_bot')


class MockedSession(BaseSession):
    """Answers Bot API calls locally and records them, so handlers can be driven
    through the real Dispatcher without touching Telegram."""

    def __init__(self):
        super().__init__()
        self.calls: list[TelegramMethod] = []
        self._message_id = 1000

    async def close(self):
        pass

    async def make_request(self, bot: Bot, method: TelegramMethod, timeout: Optional[int] = None) -> Any:
        self.calls.append(method)
        return self._response(bot, method)

    async def stream_content(self, url: str, headers=None, timeout: int = 30,
                             chunk_size: int = 65536, raise_for_status: bool = True):
        yield b''

    def _response(self, bot: Bot, method: TelegramMethod) -> Any:
        name = type(method).__name__
        if name in ('SendMessage', 'CopyMessage', 'SendDocument', 'SendPoll'):
            return self._message(method)
        if name == 'GetMe':
            return BOT_USER
        return True

    def _message(self, method: TelegramMethod) -> Message:
        self._message_id += 1
        chat_id = getattr(method, 'chat_id', 1)
        poll = None
        if type(method).__name__ == 'SendPoll':
            poll = Poll(id='poll1', question=method.question, is_closed=False, is_anonymous=False,
                        type='quiz', allows_multiple_answers=False, total_voter_count=0,
                        options=[PollOption(text=o, voter_count=0) for o in method.options],
                        correct_option_id=method.correct_option_id)
        return Message(message_id=self._message_id, date=datetime.datetime.now(),
                       chat=Chat(id=chat_id, type='private'), from_user=BOT_USER,
                       text=getattr(method, 'text', None), poll=poll)

    # --- helpers for assertions -------------------------------------------------

    def sent_texts(self) -> list[str]:
        return [c.text for c in self.calls if type(c).__name__ == 'SendMessage']

    def polls(self) -> list[TelegramMethod]:
        return [c for c in self.calls if type(c).__name__ == 'SendPoll']

    def method_names(self) -> list[str]:
        return [type(c).__name__ for c in self.calls]

    def clear(self):
        self.calls.clear()


def make_user(user_id: int, first_name: str = 'Tester', lg: str = 'en') -> User:
    return User(id=user_id, is_bot=False, first_name=first_name,
                username=f'tester{user_id}', language_code=lg)


def message_update(user: User, text: str, update_id: int = 1) -> Update:
    return Update(update_id=update_id, message=Message(
        message_id=update_id, date=datetime.datetime.now(),
        chat=Chat(id=user.id, type='private'), from_user=user, text=text))


def callback_update(user: User, data: str, update_id: int = 1) -> Update:
    return Update(update_id=update_id, callback_query=CallbackQuery(
        id=str(update_id), from_user=user, chat_instance='test', data=data,
        message=Message(message_id=update_id, date=datetime.datetime.now(),
                        chat=Chat(id=user.id, type='private'), from_user=BOT_USER)))
