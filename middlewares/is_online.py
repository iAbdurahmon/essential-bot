from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from tools.db_conn import cur, conn
from tools.time_file import timefunc


class IsOnline(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        today_time = f"{timefunc('today')}/{timefunc('time')}"
        # one statement per update: touch last_use and pick up a renamed account
        cur.execute('UPDATE users SET last_use = %s, name = %s WHERE tg_id = %s',
                    (today_time, user.first_name, str(user.id)))
        conn.commit()
        return await handler(event, data)
