import sys
from datetime import datetime
from threading import Thread
import socket


#prints out the missing or incorrect arg and exits program
def error(arg):
    sys.exit("ERR - arg " + arg)
    
#checks if server allowed the nickname and client ID
def valid_nickname_id():
    global nickname, client_ID
    server_message = client_socket.recv(1024).decode()
    #split and insert message parts into a dict
    message_parts = server_message[1:-1].split(", ")
    message = {}
    for x in message_parts:
        key, value = x.split(":", 1)
        message[key.strip('"')] = value.strip('" ')
    #if type was "error" then nickname or clientID was not unique and client ask user to input a new one
    if message.get("type") == "error":
        if message.get("message") == "Nickname already in use":
            nickname = input("Nickname already in use. Choose another nickname:\n")
        else:
            client_ID = input("ClientID already in use. Choose another ClientID:\n")
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_sentence = f'{{"type": "nickname", "nickname": "{nickname}", "clientID": "{client_ID}", "timestamp":"{dt}"}}'
        client_socket.send(client_sentence.encode())
        return False
    return True

#reads messages from server
def listen_for_msg():
    global msg_rcv, msg_sent,char_rcv, char_sent
    while True:
        server_message = client_socket.recv(1024).decode()
        #stop reading when server sends disconnected and close socket
        if server_message == "disconnected":
            break
        message_parts = server_message[1:-1].split(", ")
        message = {}
        for x in message_parts:
            key, value = x.split(":", 1)
            message[key.strip('"')] = value.strip('" ')

        print(f"{message['timestamp']} :: {message['nickname']}: {message['message']}")
        msg_rcv+=1
        char_rcv+=len(message["message"])
        
    client_socket.close()
    end_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'“Summary: start:{start_dt} end:{end_dt}, msg sent:{msg_sent}, msg rcv:{msg_rcv}, char sent:{char_sent}, char rcv:{char_rcv}”')
    
#sends messages to server
def send_message():
    global msg_sent, char_sent
    while True:
        user_input = input()
        print()
        #stops loop when user enters disconnect
        if (user_input == "disconnect"):
            client_message = f'{{"type": "disconnect", "nickname": "{nickname}", "clientID": "{client_ID}"}}'
            client_socket.send(client_message.encode())
            break;
            
        else:
            #sends message to other clients
            dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            client_message = f'{{"type": "message", "nickname": "{nickname}", "message": "{user_input}", "timestamp": "{dt}"}}'
            client_socket.send(client_message.encode())
            msg_sent+=1
            char_sent+=len(user_input)
                  
                  
                  
#checks if the server IP is missing           
try:
    #checks if the input server IP is host name or IP address
    if sys.argv[1] == "egr-v-cmsc440-1.rams.adp.vcu.edu":
        ip = socket.gethostbyname(sys.argv[1])
    elif sys.argv[1] == "10.0.0.1":
        ip = sys.argv[1]
    #if not either, print error and exit
    else:
        error("1")
except:
    error("1")
    
#checks if the port is missing or is not an int
try:
    port = int(sys.argv[2])
except:
    error("2")
    
#checks if the nickname is missing or is not a string
try:
    if sys.argv[3].isalpha():    
        nickname = sys.argv[3]
    else:
        error("3")
except IndexError:
    error("3")
    
#checks if the client ID is missing or is not an int
try:
    if sys.argv[4].isdigit():
        client_ID = sys.argv[4]
    else:
        error("4")
except IndexError:
    error("4")
    
msg_sent = msg_rcv = char_sent = char_rcv =0
#connect to the server socket
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client_socket.connect((ip, port))
start_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"ChatClient started with server IP: {ip}, port: {port}, nickname: {nickname}, client ID: {client_ID}, Date/Time: {start_dt}")
dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
client_sentence =f'{{"type": "nickname", "nickname": "{nickname}", "clientID": "{client_ID}", "timestamp":"{dt}"}}'
client_socket.send(client_sentence.encode())
#loops until the client nickname and ID is unique
while not(valid_nickname_id()):
    pass
#creates thread that listens for messages from server
thread = Thread(target = listen_for_msg)
thread.start()
#main thread sends messages to server
print("Enter message:\n")
send_message()
thread.join()
