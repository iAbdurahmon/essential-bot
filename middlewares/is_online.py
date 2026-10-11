from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message

from tools.db_conn import cur, conn
from tools.time_file import timefunc


class IsOnline(BaseMiddleware):
    def checker(self, tg_id):
        today = timefunc('today')
        time = timefunc('time')
        today_time = f"{today}/{time}"
        cur.execute('UPDATE users SET last_use = %s WHERE tg_id = %s', (today_time, tg_id))
        conn.commit()

    def namer(self, name, tg_id):
        cur.execute('SELECT name FROM users WHERE tg_id = %s', (tg_id,))
        result = cur.fetchone()
        if result:
            name_db = result[0]
            if name_db != name:
                cur.execute('UPDATE users SET name = %s WHERE tg_id = %s', (name, tg_id))
                conn.commit()
                print('name updated')
        else:
            print(f"No user found with tg_id: {tg_id}")

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user = data["event_from_user"]
        user_id = str(user.id)
        name = user.first_name
        self.checker(tg_id=user_id)
        self.namer(name=name, tg_id=user_id)
        print('ok')
        result = await handler(event, data)
        return result
