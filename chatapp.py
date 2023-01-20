#!/usr/bin/env python3
import sys
import socket
import selectors
import types


class Server:

    def __init__(self):
        self.sel = selectors.DefaultSelector()
        self.users = {
            "alice": "password1",
            "bob": "password2",
        }

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read

        print(f"Accepted connection from {addr}")
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"", auth=False)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask, events):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data and not data.auth:  # client not yet authorized
                # parse auth header
                auth_header = recv_data.decode().rstrip(" \n").split(",")
                if len(auth_header) != 3 or auth_header[0] != "auth":
                    print("Invalid auth header.")
                    print(f"Closing connection to {data.addr}")
                    self.sel.unregister(sock)
                    sock.close()
                elif auth_header[1] not in self.users:
                    print(f"User {auth_header[1]} not exist.")
                    print(f"Closing connection to {data.addr}")
                    self.sel.unregister(sock)
                    sock.close()
                elif auth_header[2] == self.users[auth_header[1]]:    # username and pw match
                    data.auth = True
                else:
                    print(f"Invalid password, failed to auth.")
                    print(f"Closing connection to {data.addr}")
                    self.sel.unregister(sock)
                    sock.close()

            elif recv_data:
                print(f"Received {recv_data!r}")
                client_keys = [e[0] for e in events if e[0].data is not None]
                for client in client_keys:
                    # filter out client that sent the data
                    if client.fileobj != sock:
                        client.data.outb += recv_data
            else:
                print(f"Closing connection to {data.addr}")
                self.sel.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                print(f"Echoing {data.outb!r} to {data.addr}")
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def main(self, host, port):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, port))
        lsock.listen()
        print(f"Listening on {(host, port)}")
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        self.service_connection(key, mask, events)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()


class Client:

    def __init__(self):
        self.sel = selectors.DefaultSelector()
        username = input("Enter your username: ")
        self.username = username
        password = input("Enter your password: ")
        self.password = password

    def start_connections(self, host, port):
        server_addr = (host, port)

        print(f"Starting connection to {server_addr}")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.setblocking(False)
        sock.connect_ex(server_addr)

        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        auth_string = f"auth,{self.username},{self.password}"
        network_data = types.SimpleNamespace(
            name="network",
            outb=auth_string.encode()
        )
        stdin_data = types.SimpleNamespace(
            name="stdin"
        )
        self.sel.register(sock, events, data=network_data)
        self.sel.register(sys.stdin, selectors.EVENT_READ, data=stdin_data)

    def prompt(self):
        print(f"[{self.username}] ", end='')
        sys.stdout.flush()

    def service_connection(self, key, mask, events):
        sock = key.fileobj
        data = key.data

        if mask & selectors.EVENT_READ:
            if data.name == "network":  # received data from network
                recv_data = sock.recv(1024)  # Should be ready to read
                if recv_data:
                    print(f"\n{recv_data.decode()}", end='')
                    self.prompt()
                if not recv_data:
                    print("Server has closed the connection.")
                    self.sel.unregister(sock)
                    sock.close()

            elif data.name == "stdin":  # received data from user input
                recv_data = sock.readline()
                msg = f"[{self.username}] {recv_data}".encode()
                client_keys = [e[0] for e in events if e[0].data.name == "network"]
                for client in client_keys:
                    # filter out client that sent the data
                    if client.fileobj != sock:
                        client.data.outb += msg
                self.prompt()

        if mask & selectors.EVENT_WRITE:
            if data.outb:
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def main(self, host, port: int):
        self.start_connections(host, port)
        self.prompt()

        try:
            while True:
                events = self.sel.select(timeout=1)
                if events:
                    for key, mask in events:
                        self.service_connection(key, mask, events)
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("Caught keyboard interrupt, exiting")
        finally:
            self.sel.close()


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <server/client> <host> <port>")
        sys.exit(1)

    selection, host, port = sys.argv[1:4]
    if selection == "server":
        s = Server()
        s.main(host, int(port))
    elif selection == "client":
        c = Client()
        c.main(host, int(port))
    else:
        print(f"Usage: {sys.argv[0]} <server/client> <host> <port>")
        sys.exit(1)

