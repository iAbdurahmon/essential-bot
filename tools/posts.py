from tools.db_conn import cur, conn
from tools.time_file import timefunc


def save_post(table: str, version: str, lg: str, msg_id: int):
    today_time = f"{timefunc('today')}/{timefunc('time')}"
    cur.execute(f"INSERT INTO {table} (date, version, lg, msg_id) VALUES (%s, %s, %s, %s)",
                (today_time, version, lg, msg_id))
    conn.commit()


def last_post(table: str):
    cur.execute(f"SELECT version, lg, msg_id FROM {table} ORDER BY id DESC LIMIT 3")
    rows = cur.fetchall()
    if len(rows) < 3:
        return None, {}
    version = rows[0][0]
    msg_ids = {lg: msg_id for _, lg, msg_id in rows}
    return version, msg_ids
