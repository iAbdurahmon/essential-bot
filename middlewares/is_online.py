from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from tools.db_conn import execute


class IsOnline(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        # one statement per update: touch last_use and pick up a renamed account
        execute('UPDATE users SET last_use = now(), name = %s WHERE tg_id = %s',
                (user.first_name, user.id))
        return await handler(event, data)
