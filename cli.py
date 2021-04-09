import atexit

from services.config import MessageState
import services.redis_connection as redis

redis.connect()

from services.user import User

current_user = None

def exit_handler():
    global current_user
    if current_user:
        del current_user
    print('Bye!')

atexit.register(exit_handler)

print("Hi!")

while True:
    try:
        user_input = input(">> ")
        words = list(filter(lambda word: word and not word.isspace(), user_input.split(' ')))
        verb = words[0].lower()
        if verb == 'exit':
            break
        if verb == 'login':
            if len(words) < 2:
                print("You have to provide the username")
                continue
            if len(words) > 3:
                print("The command takes only up to three arguments")
                continue
            username = words[1].lower()
            if len(words) == 3:
                if words[2].lower() != '--admin':
                    print('Unsupported option: ' + words[2])
                    continue
                else:
                    current_user = User(username, True)
                    continue
            else:
                current_user = User(username)
                continue
        if verb == 'send':
            if not current_user:
                print("You have to log in first")
                continue
            content = input("Message >> ")
            recipient = input("To >> ")
            if current_user.send_message(content, recipient):
                print("Sent!")
            else:
                print("The recipient you've specified does not exist!")
            continue
        if verb == 'whoami':
            if current_user:
                print(current_user.username)
            else:
                print("Unauthorized")
            continue
        if verb == 'logout':
            del current_user
            current_user = None
            continue
        if verb == 'list':
            if not current_user:
                print("Unauthorized")
                continue
            if len(words) < 2:
                print('You should specify the subject to list')
                continue
            subject = words[1].lower()
            if subject == 'messages':
                if len(words) < 3:
                    print('You should specify the type of messages')
                    continue
                type = words[2].lower()
                if type == 'status':
                    res = current_user.get_send_messages_amount_by_status()
                    print("Created:", res[MessageState.CREATED])
                    print("In the queue:", res[MessageState.IN_THE_QUEUE])
                    print("On spam check:", res[MessageState.SPAM_CHECK])
                    print("Blocked by spam filter:", res[MessageState.BLOCKED])
                    print("Sent:", res[MessageState.SENT])
                    print("Delivered:", res[MessageState.DELIVERED])
                    print("Messages sent in general:", res["amount"])
                    continue
                if type not in 'sent received':
                    print('Type unsupported')
                    continue
                inp = input("Number >> ")
                number = None
                try:
                    number = int(inp)
                    if number < 1:
                        raise Exception()
                except:
                    print("You should enter a positive number")
                    continue
                username = current_user.username
                if current_user.admin:
                    username = input("By >> ")
                if type == 'sent':
                    messages = User.read_last_messages_sent(number, username)
                    print("STATUS\tRECIPIENT\tCONTENT")
                    for message in messages:
                        print (message["status"], message["recipient"], message["content"], sep="\t")
                else:
                    messages = User.read_last_messages_received(number, username)
                    print("SENDER\tCONTENT")
                    for message in messages:
                        print (message["sender"], message["content"], sep="\t")
                
                continue
            if not current_user.admin:
                print("Forbidden")
                continue
            if subject == 'log':
                if len(words) < 3:
                    print("You should specify kind of the log")
                    continue
                kind = words[2].lower()
                inp = input("Number >> ")
                number = None
                try:
                    number = int(inp)
                    if number < 1:
                        raise Exception()
                except:
                    print("You should enter a positive number")
                    continue
                if kind == 'spam':
                    log = User.list_spam_logs(number)
                else:
                    log = User.list_logs(number)
                for record in log:
                    print(record)
                continue
            if subject == 'online':
                users = User.list_online()
                for record in users:
                    print(record)
                continue
            if subject == 'active':
                inp = input("Number >> ")
                number = None
                try:
                    number = int(inp)
                    if number < 1:
                        raise Exception()
                except:
                    print("You should enter a positive number")
                    continue
                users = User.list_active(number)
                for record in users:
                    print(record)
                continue
            if subject == 'spammers':
                inp = input("Number >> ")
                number = None
                try:
                    number = int(inp)
                    if number < 1:
                        raise Exception()
                except:
                    print("You should enter a positive number")
                    continue
                users = User.list_spammers(number)
                for record in users:
                    print(record)
                continue
        if verb == 'logout':
            del current_user
        print("Unsupported command: " + user_input)
    except KeyboardInterrupt:
        break
    except Exception as err:
        print(err)
        print("Server is unreachable!")
        break

        

