import psycopg2
from pymongo import MongoClient

dbname = 'essential'
user = 'bardo_admin'
password = '0046'
host = 'localhost'
# 45.10.161.251

try:
    conn = psycopg2.connect(database=dbname, user=user, password=password, host=host)
    cur = conn.cursor()
    print('Connected')
except Exception as e:
    print(e)


username = "admin"  #
password = "41964196"  #
hostname = "localhost"  #
port = 27017  #
auth_db = "admin"  #
connection_string = f"mongodb://{username}:{password}@{hostname}:{port}/{auth_db}"  #

client = MongoClient(connection_string)  #
db = client['essential']  #
collection = db['users']  #

