class Redis:
    HOST = '10.2.14.254'
    PORT = 31048
    PASSWORD = 'a-very-complex-password-here'

class Keys:
    USERS_SET = "users"
    ONLINE_USERS = "users_online"
    NEW_MESSAGES_CHANNEL = "new_message_channel"
    SPAM_CHANNEL = "spam_channel"
    LOG_CHANNEL = "log_channel"
    LOG_LIST = "log"
    SPAM_LIST = "spam_list"
    SPAM_COUNTER = "spam_counter"
    MESSAGES_QUEUE = "queue"
    MESSAGE_HASH = "message"
    LAST_MESSAGE_ID = "last_message_id"
    SENT_MESSAGES_LIST = "sent_messages"
    RECEIVED_MESSAGES_LIST = "received_messages"

class UserType:
    ADMIN_USER_LABEL = "admin"
    USER_LABEL = "user"

class MessageState:
    CREATED = 'CREATED'
    IN_THE_QUEUE = 'IN THE QUEUE'
    SPAM_CHECK = 'SPAM CHECK'
    BLOCKED = 'BLOCKED'
    SENT = 'SENT'
    DELIVERED = 'DELIVERED'

class Const:
    ADDED_TO_QUEUE_NOTIFICATION = "8"
    SPAM_DELAY = 1