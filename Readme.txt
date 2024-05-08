Erick Zheng V#00984172


ChatClient.py

To compile using Python 3: "python3 ChatClient.py [server IP/hostname] [port number] [nickname] [clientID]"

1. ChatClient requires 4 command line arguments: server hostname/IP, port number of server, nickname, clientID
NOTE: server only runs on IP: 10.0.0.1, port number and clientID must only contain integer, and nickname must only contain letters 
2. If any of the arguments are missing or incorrect, retry with correct arguments
3. Client will create socket and connect to server with the input server IP and port number
4. If nickname or clientID is not unique, server will send a message telling client, and client will prompt user for a different nickname or clientID
5. Upon approval of nickname and ID, the client is now connected and user can send messages using the CLI and messages sent by other clients will pop up
6. If user wishes to disconnect, enter "disconnect" in the command line



ChatServer.py

To compile using Python 3: "python3 ChatServer.py [port number]"

1. ChatServer requires 1 command line argument: port number
NOTE: port number must be a positive integer less than 65536
2. Server will send and receive messages based on the messages it receives from client(s)
3. To terminate the server, press CRTL-C to send SIGINT signal



