import socket
import asyncio
import json

class Server:
    def __init__(self):
        self.c = ConsoleColors()
        self.connections = []  # List to store active connections
        self.connected_users = []  # List to store connected users
        
        # Get host and port from user
        self.host, self.port = self.getHostAndIp()
        
        # Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(False)  # Set to non-blocking mode
        self.server_socket.bind((self.host, self.port))

        # Start listening to incoming connections
        self.server_socket.listen()
        print(f"{self.c.OKGREEN}Server is listening on {self.c.BOLD}{self.host}:{self.port}{self.c.ENDC}")

        # Run the asyncio event loop to handle connections
        asyncio.run(self.acceptConnections())

    async def acceptConnections(self):
        while True:
            try:
                # Accept incoming connections
                conn, addr = await asyncio.get_event_loop().sock_accept(self.server_socket)
                print(f"{self.c.OKGREEN}Connected by {self.c.BOLD}{addr}{self.c.ENDC}")
                self.connections.append(conn)

                # Create a new task to handle the connection
                asyncio.create_task(self.handleConnection(conn))
            except Exception as e:
                print(f"{self.c.FAIL}Error accepting connections: {e}{self.c.ENDC}")

    async def handleConnection(self, conn):
        while True:
            try:
                # Receive data from the client
                data = await asyncio.get_event_loop().sock_recv(conn, 1024)
                if not data:
                    print(f"{self.c.FAIL}Client disconnected{self.c.ENDC}")
                    conn.close()  # Close the connection
                    self.connections.remove(conn)  # Remove the connection from the list
                    break

                # Decode the data from bytes to string
                data = data.decode()

                print(f"{self.c.OKCYAN}Received: {len(data.encode('utf-8'))} Bytes{self.c.ENDC}")

                try:
                    # Parse the JSON string into a dictionary
                    data = json.loads(data)
                except json.JSONDecodeError as e:
                    print(f"{self.c.FAIL}Error decoding JSON: {e}{self.c.ENDC}")
                    continue

                # Extract username and message from the JSON data
                username = data.get("username")
                usermessage = data.get("message")

                if username and usermessage:
                    # Broadcast the message to all other clients
                    self.connected_users.append(username)

                    await self.sendToAll(conn, json.dumps({"username": username, "message": usermessage}))
                else:
                    print(f"{self.c.FAIL}Invalid data received{self.c.ENDC}")
            except Exception as e:
                print(f"{self.c.FAIL}Error receiving data: {e}{self.c.ENDC}")
                conn.close()  # Close the connection on error
                self.connections.remove(conn)  # Remove the connection from the list
                break

    async def sendToAll(self, sender_conn, message):
        # Broadcast the message to all connected clients except the sender
        for conn in self.connections:
            if conn != sender_conn:
                try:
                    await asyncio.get_event_loop().sock_sendall(conn, message.encode())
                except Exception as e:
                    print(f"{self.c.FAIL}Error sending message: {e}{self.c.ENDC}")
                    conn.close()  # Close the connection on error
                    self.connections.remove(conn)  # Remove the connection from the list

    def getHostAndIp(self):
        # Get host and port from user input
        host = input(f"Enter host address (on for local use -> 'localhost'):{self.c.HEADER} ")
        print(f"\033[{self.c.ENDC}")
        
        is_int = True
        while is_int:
            try:
                port = int(input(f"Enter port:{self.c.HEADER} "))
                print(f"\033[{self.c.ENDC}")
                is_int = False
            except ValueError:
                print(f"{self.c.FAIL}Please enter a valid port{self.c.ENDC}")
                continue

        return host, port

class ConsoleColors:
    # Console color codes for better output formatting
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':
    # Start the server
    Server()