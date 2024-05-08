import sys
import socket
import signal
from datetime import datetime
from threading import Thread

#Connection object stores information about client
class Connection:
    def __init__(self, connection_socket, addr, nickname, id):
        self.connection_socket = connection_socket
        self.ip, self.port = addr
        self.nickname = nickname
        self.id = id
        
#signal handler used to detect SIGINT signal
def handler(sig, frame):
    global exit
    #stops the loop in the main thread
    exit = True
    
#broadcast client message to all other clients
def broadcast(client_socket, message, connection_obj):
    index = connection_list.index(connection_obj)
    print(f'"Received: IP:{connection_list[index].ip}, Port:{connection_list[index].port}, Client-Nickname:{message["nickname"]}, ClientID:{connection_list[index].id}, Date/Time:{message["timestamp"]}, Msg-Size:{len(message["message"])}"')
    broadcast_list = list()
    broadcasted_clients = ""
    #iterate through all active connections
    for obj in connection_list:
        if obj.connection_socket != client_socket:
            broadcast_msg = f'{{"timestamp": {message["timestamp"]}, "nickname": {message["nickname"]}, "message": {message["message"]}}}'
            #error handling for if a client was recently forcefully terminated
            try:
                obj.connection_socket.send(broadcast_msg.encode())
            except:
                #server continues to broadcast the message to the subsequent clients in case of errors
                continue
            broadcast_list.append(obj.nickname)
            broadcasted_clients = ", ".join(broadcast_list)
    print(f'"Broadcasted: {broadcasted_clients}"\n')
    
#checks if client nickname is unique by going through list of active connections
def available_nickname(client_socket, message):
    for obj in connection_list:
        if (obj.nickname == message["nickname"]):
            send_message = '{"type": "error", "message": "Nickname already in use"}'
            try:
                client_socket.send(send_message.encode())  
            except:
                pass
            finally:
                return False
    return True

#checks if client ID is unique by going throught eh list of active connections
def unique_client_id(client_socket, message):
    for obj in connection_list:
        if (obj.id == message["clientID"]):
            send_message = '{"type": "error", "message": ClientID already in use"}'
            try:
                client_socket.send(send_message.encode())
            except:
                pass
            finally:
                return False
    return True

#remove client from list of active connections
def disconnected(client_socket, message, connection_obj):
    dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f'"{dt} :: {message["nickname"]}: disconnected."')
    connection_list.remove(connection_obj)
    #error handling for if client was recently forcefully terminated
    try:
        client_socket.send("disconnected".encode())
    except:
        pass
    
#receives messages from client and sends messages based on the type of messages server received
def receive_client_msg(client_socket, port):
    disconnect = False
    while not disconnect:
        try:
            client_message = client_socket.recv(1024).decode()
            #if client message is empty, the client was forcefully terminated
            if not client_message:
                #remove client from list of active connection and close the socket
                connection_list.remove(connection_obj)
                break;
        except:
            connection_list.remove(connection_obj)
            break;
        message_parts = client_message[1:-1].split(", ")
        message = {}
        for x in message_parts:
            key, value = x.split(":", 1)
            message[key.strip('"')] = value.strip('" ')
        if message["type"] == "nickname":
            #if not unique client ID, go to next iteration and wait for client to send another message
            if not unique_client_id(client_socket, message):
                continue
            if available_nickname(client_socket, message):
                print(f"{message['timestamp']} :: {message['nickname']}: connected.")
                connection_obj = Connection(client_socket, addr, message["nickname"], message["clientID"])
                connection_list.append(connection_obj)
                client_socket.send('{"type": "approve", "message": "Nickname registered"}'.encode())
            else:
                #if not a unique nickname, go to next iteration and wait for client message
                continue
        elif message["type"] == "message":
            broadcast(client_socket, message, connection_obj)
        elif message["type"] == "disconnect":
            disconnected(client_socket, message, connection_obj)
            #breaks loop
            disconnect = True
    client_socket.close()
    
        
ip = '10.0.0.1'
if len(sys.argv) != 2:
    sys.exit("ERR - arg 1")
   
try:
    port = int(sys.argv[1])   # test if int
except ValueError:
    sys.exit("ERR - arg 1") 
    
if not(port > 0 and port < 65536):
    sys.exit("ERR - arg 1")

#creates a welcome socket with IP and port number
try:
    welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcome_socket.bind((ip, port))
    print(f"ChatServer started with server IP: {ip}, port: {port} ...\n.\n.\n.")

except socket.error:
    print(f"ERR - cannot create ChatServer socket using port number {port}")
    sys.exit()
    
welcome_socket.listen(5)
connection_list = list()
signal.signal(signal.SIGINT, handler)
exit = False
welcome_socket.settimeout(5)
#continues to run until SIGINT signal is sent, socket will check condition once every 5 seconds at most
while not exit:
    try:
        connection_socket, addr = welcome_socket.accept()
    except socket.timeout:
        continue
    #creates separate thread for each client connection
    thread = Thread(target = receive_client_msg, args = (connection_socket, addr))
    #terminates threads when main thread termiantes
    thread.daemon = True
    thread.start()
welcome_socket.close()
    
    
    