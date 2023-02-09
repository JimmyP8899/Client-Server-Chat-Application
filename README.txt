# Client-Server Chat Application

The Chat Server and Client project is a networking application that allows multiple clients to connect to a server and communicate with each other. The server has the ability to accept connections from up to 10 clients, accept messages from clients, and broadcast the messages to the rest of the clients. Clients are able to connect and disconnect from the server and send messages to the server for broadcast. The project also includes basic security measures, such as implementing SSL/TLS to secure connections and allowing users to authenticate with a username and password.

# Program Usage:

# Running the Chat Server

To run the chat server, navigate to the directory where the chat_app.py file is located and enter the following command in the terminal:

python3 chat_app.py server 127.0.0.1 9008

Replace 127.0.0.1 with the IP address of the server, and 9008 with the desired port number.

# Running the Chat Client

To run the chat client, navigate to the directory where the chat_app.py file is located and enter the following command in the terminal:

python3 chat_app.py client 127.0.0.1 9008

Replace 127.0.0.1 with the IP address of the server, and 9008 with the port number used by the server.
