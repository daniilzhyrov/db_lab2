from services.redis_connection import connection as redis
from services.config import UserType, Keys, MessageState, Const
import json
import time
import random
import string

class User:
    def __init__(self, username: str, admin: bool = False):
        # perform login
        self.username = username
        self.admin = admin
        redis.set(Keys.USERS_SET + ":" + username, UserType.ADMIN_USER_LABEL if admin else UserType.USER_LABEL)
        redis.sadd(Keys.ONLINE_USERS, username)
        log_mes = "User " + self.username + " logged in at " + time.ctime()
        redis.publish(Keys.LOG_CHANNEL, log_mes)
        redis.lpush(Keys.LOG_LIST, log_mes)
        
    def __del__(self):
        # perform logout
        log_mes = "User " + self.username + " logged out at " + time.ctime()
        redis.publish(Keys.LOG_CHANNEL, log_mes)
        redis.lpush(Keys.LOG_LIST, log_mes)
        redis.srem(Keys.ONLINE_USERS, self.username)

    def __get_new_message_id():
        return redis.incr(Keys.LAST_MESSAGE_ID)
    
    def send_message(self, content, recipient) -> bool:
        if not redis.get(Keys.USERS_SET + ":" + recipient):
            return False
        
        message_id = User.__get_new_message_id()
        
        redis.hmset(Keys.MESSAGE_HASH + ":" + str(message_id), {
            "sender": self.username,
            "content": content,
            "recipient": recipient,
            "status": MessageState.CREATED
        })
        redis.publish(Keys.NEW_MESSAGES_CHANNEL, Const.ADDED_TO_QUEUE_NOTIFICATION)
        redis.rpush(Keys.MESSAGES_QUEUE, message_id)
        redis.lpush(Keys.SENT_MESSAGES_LIST + ":" + self.username, message_id)
        redis.hmset(Keys.MESSAGE_HASH + ":" + str(message_id), {
            "status": MessageState.IN_THE_QUEUE
        })
        return True
    
    def read_last_messages_sent(number : int, username : str) -> [dict]:
        message_ids = redis.lrange(Keys.SENT_MESSAGES_LIST + ":" + username, 0, number)
        messages = []
        for mes_id in message_ids:
            response = redis.hmget(Keys.MESSAGE_HASH + ":" + mes_id, ["content", "recipient", "status"])
            messages.append({
                "content" : response[0],
                "recipient" : response[1],
                "status" : response[2]
            })
        return messages

    def read_last_messages_received(number : int, username : str) -> [dict]:
        message_ids = redis.lrange(Keys.RECEIVED_MESSAGES_LIST + ":" + username, 0, number)
        messages = []
        for mes_id in message_ids:
            redis.hset(Keys.MESSAGE_HASH + ":" + mes_id, "status", MessageState.DELIVERED)
            response = redis.hmget(Keys.MESSAGE_HASH + ":" + mes_id, ["content", "sender"])
            messages.append({
                "content" : response[0],
                "sender" : response[1],
            })
        return messages
    
    def list_logs(number: int) -> [str]:
        return redis.lrange(Keys.LOG_LIST, 0, number)

    def list_spam_logs(number: int) -> [str]:
        return redis.lrange(Keys.SPAM_LIST, 0, number)
    
    def list_online() -> [str]:
        return redis.smembers(Keys.ONLINE_USERS)
    
    def list_active(number: int) -> [str]:
        KEY = "active_set"
        redis.delete(KEY)
        for username in User.list_online():
            count = redis.llen(Keys.SENT_MESSAGES_LIST + ":" + username)
            redis.zadd(KEY, {username : count})
        return redis.zrevrange(KEY, 0, number)

    def list_spammers(number: int) -> [str]:
        return redis.zrevrange(Keys.SPAM_COUNTER, 0, number)

    def get_send_messages_amount_by_status(self):
        res = {
            MessageState.CREATED : 0,
            MessageState.IN_THE_QUEUE : 0,
            MessageState.SPAM_CHECK: 0,
            MessageState.BLOCKED: 0,
            MessageState.SENT : 0,
            MessageState.DELIVERED : 0
        }
        message_ids = message_ids = redis.lrange(Keys.SENT_MESSAGES_LIST + ":" + self.username, 0, -1)
        for mes_id in message_ids:
            response = redis.hget(Keys.MESSAGE_HASH + ":" + mes_id, "status")
            res[response] += 1
        res["amount"] = len(message_ids)
        return res
        