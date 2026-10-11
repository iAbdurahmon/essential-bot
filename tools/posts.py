from tools.db_conn import fetch_all, execute


def save_post(table: str, version: str, lg: str, msg_id: int):
    execute(f"INSERT INTO {table} (date, version, lg, msg_id) VALUES (now(), %s, %s, %s)",
            (version, lg, msg_id))


def last_post(table: str):
    rows = fetch_all(f"SELECT version, lg, msg_id FROM {table} ORDER BY id DESC LIMIT 3")
    if len(rows) < 3:
        return None, {}
    version = rows[0][0]
    msg_ids = {lg: msg_id for _, lg, msg_id in rows}
    return version, msg_ids
