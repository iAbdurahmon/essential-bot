import logging

import psycopg2
from pymongo import MongoClient

from config_reader import config

logger = logging.getLogger(__name__)

conn = psycopg2.connect(
    database=config.db_name,
    user=config.db_user,
    password=config.db_password.get_secret_value(),
    host=config.db_host,
    port=config.db_port
)
cur = conn.cursor()
logger.info('postgres connected: %s@%s', config.db_name, config.db_host)

client = MongoClient(config.mongo_uri)
db = client[config.mongo_db]
collection = db['users']
