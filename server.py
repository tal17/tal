import socket
import hashlib
import threading
import random
import string
import datetime

my_lock = threading.Lock()


def check_if_username_exists(user_name):
    my_lock.acquire()
    with open("accounts.txt", "r") as accounts:
        account_data = accounts.read()
        users = account_data.split("\r\n")
        for i in range(len(users)):
            x = users[0]
            name = x.split("~")[0]
            if name == user_name:
                return False
    my_lock.release()
    return True


def create_salt():
    salt_len = 16
    salt = ""
    options = string.ascii_uppercase + string.digits + string.ascii_lowercase
    for i in range(salt_len):
        salt += options[random.randint(0,len(options)-1)]
    return salt


def main_thread(client_socket,i):
    while True:
        user_data = client_socket.recv(1024)
        user_data = user_data.split("~")
        if len(user_data) != 3:
            client_socket.send("Unknown Command")
            client_socket.close()
            break
        if user_data[0] != "REG" and user_data[0] != "LOG":
            client_socket.send("Unknown Command")
            client_socket.close()
            break
        if user_data[0] == "REG":
            user_name, password = user_data[1], user_data[2]
            if check_if_username_exists(user_name) == False:
                client_socket.send("This username is already taken")
                client_socket.close()
                break
            salt = create_salt()
            to_hash = password + salt
            salted_hash = hashlib.sha256(to_hash.encode()).hexdigest()
            my_lock.acquire()
            with open("accounts.txt", "r") as accounts:
                x = accounts.read()
                x += user_name+"~"+salted_hash+"~"+salt+"~"+datetime.datetime.now().strftime('%d/%m/%Y %H:%M')+"\n"
            with open("accounts.txt", "w") as accounts:
                print x
                accounts.write(x)
            my_lock.release()
            client_socket.send("Registered Successfully")
        elif user_data[0] == "LOG":
            user_name, password = user_data[1], user_data[2]
            with open("accounts.txt", "r") as accounts:
                x = accounts.read()
                x = x.split("\n")
                real_password = ""
                real_salt = ""
                name_exists = False
                for user in x:
                    name = user.split("~")[0]
                    if name == user_name:
                        details = user.split("~")
                        name_exists = True
                        real_password = details[1]
                        real_salt = details[2]
                if name_exists == False:
                    client_socket.send("Incorrect Username")
                    client_socket.close()
                    break
                to_check = password + real_salt
                if hashlib.sha256(to_check.encode()).hexdigest() == real_password:
                    client_socket.send("LOGIN SUCCESSFULLY")


def main():
    threads = []
    i = 0
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(100)
    while True:
        i += 1
        (client_socket, client_address) = server_socket.accept()
        t = threading.Thread(target=main_thread, args=(client_socket, i))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == '__main__':
    main()