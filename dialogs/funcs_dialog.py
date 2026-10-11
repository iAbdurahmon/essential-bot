from aiogram.types import Message, User

from tools.db_conn import cur


def top_checker(user_id):
    cur.execute('SELECT * FROM users WHERE status = 1 ORDER BY CASE WHEN rank IS NULL THEN 1 ELSE 0 END, rank DESC')
    result = cur.fetchall()
    for num, i in enumerate(result):
        if i[3] == str(user_id):
            return num + 1


def top_all_checker():
    cur.execute('SELECT * FROM users WHERE status = 1 ORDER BY CASE WHEN rank IS NULL THEN 1 ELSE 0 END, rank DESC')
    result = cur.fetchall()
    top_data = {}
    for num, i in enumerate(result):
        top_data[num + 1] = int(i[3])
    return top_data
