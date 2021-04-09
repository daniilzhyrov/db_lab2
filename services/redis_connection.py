import redis
import sys

import services.config as config

connection = None

def connect():
    global connection
    connection = redis.Redis(host=config.Redis.HOST, port=config.Redis.PORT, db=0, password=config.Redis.PASSWORD, decode_responses=True)
    try:
        connection.ping()
    except Exception as err:
        sys.exit(err)
    