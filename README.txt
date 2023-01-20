#Description:
The project aims to implement both a chat server and client. The server will have the ability to 
accept connections from up to 10 clients, accept messages from clients, and forward those messages 
to the rest of the clients. Clients will have the ability to connect/disconnect from the server, and 
send messages to the server for broadcast. Basic security will be implemented using SSL/TLS to secure 
connections, and allowing users to authenticate with a username and password.


#Program Usage:

To Run chat application on server: python3 chat_app.py server 127.0.0.1 9008
To Run chat application on client: python3 chat_app.py client 127.0.0.1 9008





