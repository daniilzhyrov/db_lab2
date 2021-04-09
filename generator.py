import random
import string

import services.redis_connection as redis

redis.connect()

from services.user import User

print("Get N random users")
n = int(input("N >> "))
print("to send M random messages")
m = int(input("M >> "))
print("OK")

letters = string.ascii_lowercase
users = [User(''.join(random.choice(letters) for i in range(8))) for j in range(n)]

print("Generated users:")
for user in users:
    print(user.username)
print()

for i in range(n):
    current_user = users[i]
    for j in range(m):
        recipient_id = random.randint(0, len(users) - 1)
        recipient = users[recipient_id]
        message = ''.join(random.choice(letters) for i in range(8))
        print("User " + current_user.username + " sends message " + message + " to user " + recipient.username)
        current_user.send_message(message, recipient.username)