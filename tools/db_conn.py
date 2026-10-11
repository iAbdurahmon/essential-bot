import logging
from contextlib import contextmanager

from psycopg2.pool import ThreadedConnectionPool
from pymongo import MongoClient

from config_reader import config

logger = logging.getLogger(__name__)

POOL_MIN = 1
POOL_MAX = 10

pool = ThreadedConnectionPool(
    POOL_MIN, POOL_MAX,
    database=config.db_name,
    user=config.db_user,
    password=config.db_password.get_secret_value(),
    host=config.db_host,
    port=config.db_port
)
logger.info('postgres pool ready: %s@%s', config.db_name, config.db_host)


@contextmanager
def cursor(commit: bool = False):
    # one shared cursor used to serve every update: two coroutines could overwrite
    # each other's result set between execute() and fetch(). A connection per
    # statement makes that impossible.
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)


def fetch_one(sql: str, params=None):
    with cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()


def fetch_all(sql: str, params=None):
    with cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


def fetch_value(sql: str, params=None, default=None):
    row = fetch_one(sql, params)
    if not row or row[0] is None:
        return default
    return row[0]


def execute(sql: str, params=None) -> int:
    with cursor(commit=True) as cur:
        cur.execute(sql, params)
        return cur.rowcount


client = MongoClient(config.mongo_uri)
db = client[config.mongo_db]
collection = db['users']
