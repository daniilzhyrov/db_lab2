import atexit
import time
import random

import services.redis_connection
from services.config import Keys, Const, MessageState

redis_connection.connect()
redis = redis_connection.connection

def exit_handler():
    print('Bye!')

atexit.register(exit_handler)

spam_check = redis.pubsub()
spam_check.subscribe(Keys.NEW_MESSAGES_CHANNEL)


def is_spam(message: str) -> bool:
    time.sleep(Const.SPAM_DELAY)
    return bool(random.getrandbits(1))

def process_messages():
    print("Processing messages...")
    while redis.llen(Keys.MESSAGES_QUEUE):
        message_id = redis.blpop(Keys.MESSAGES_QUEUE)[1]
        redis.hset(Keys.MESSAGE_HASH + ":" + str(message_id), "status", MessageState.SPAM_CHECK)
        (content, recipient, sender) = redis.hmget(Keys.MESSAGE_HASH + ":" + str(message_id), ["content", "recipient", "sender"])
        if is_spam(content):
            spam_mes = "User " + sender + " sent spam to user " + recipient
            redis.publish(Keys.SPAM_CHANNEL, spam_mes)
            redis.lpush(Keys.SPAM_LIST, spam_mes)
            redis.zincrby(Keys.SPAM_COUNTER, float(1), sender)
            redis.hset(Keys.MESSAGE_HASH + ":" + str(message_id), "status", MessageState.BLOCKED)
        else:
            redis.lpush(Keys.RECEIVED_MESSAGES_LIST + ":" + recipient, message_id)
            redis.hset(Keys.MESSAGE_HASH + ":" + str(message_id), "status", MessageState.SENT)
    print("Messages processed!")

process_messages()

try:
    for message in spam_check.listen():
        if message.get("type") == "message":
            process_messages()
except KeyboardInterrupt:
    pass
