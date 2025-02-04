import customtkinter as ctk
from screeninfo import get_monitors
import socket
import asyncio
import json
import threading


class Main(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Variables
        self.handler = Handler()
        self.msgSpace = 50

        # Fonts
        self.enterMessageFont = ctk.CTkFont(family="Arial", size=50)

        # Window Variables
        titleText = "ChatyFy"
        self.windowWidth = self.handler.getWindowSize()[0]
        self.windowHeight = self.handler.getWindowSize()[1]

        # Set up default window
        self.title(titleText)
        self.geometry(f"{self.windowWidth}x{self.windowHeight}")
        self.resizable(0, 0)

        self.DisplayLogin()

    # Login frame
    def DisplayLogin(self):
        # Create login frame
        self.loginFrame = ctk.CTkFrame(self, width=self.windowWidth, height=self.windowHeight)
        self.loginFrame.place(x=0, y=0)
        # Login frame items
        # Login background
        self.loginBG = ctk.CTkFrame(self.loginFrame, width=self.windowWidth//2, height=self.windowHeight*0.65, fg_color="black", corner_radius=15)
        self.loginBG.place(relx=0.5, rely=0.5, anchor="center")
        # Login header
        self.header = ctk.CTkLabel(self.loginBG, text="Login to local chatroom", font=("Arial", 50), fg_color="black")
        self.header.place(relx=0.5, rely=0.1, anchor="center")
        # Username entry
        self.usernameEntry = ctk.CTkEntry(self.loginBG, width=250, height=50, placeholder_text="Username", font=("Arial", 25), bg_color="transparent", text_color="white")
        self.usernameEntry.place(relx=0.5, rely=0.25, anchor="center")
        # IP entry
        self.ipEntry = ctk.CTkEntry(self.loginBG, width=250, height=50, placeholder_text="IP Address", font=("Arial", 25), bg_color="transparent", text_color="white")
        self.ipEntry.place(relx=0.5, rely=0.40, anchor="center")
        # Port entry
        self.portEntry = ctk.CTkEntry(self.loginBG, width=250, height=50, placeholder_text="Port", font=("Arial", 25), bg_color="transparent", text_color="white")
        self.portEntry.place(relx=0.5, rely=0.55, anchor="center")
        # Login button
        self.loginBtn = ctk.CTkButton(self.loginBG, text="Login", width=250, height=50, font=("Arial", 25), command=self.ShowChatRoom)
        self.loginBtn.place(relx=0.5, rely=0.70, anchor="center")

        # Error messages
        self.errorLabel = ctk.CTkLabel(self.loginBG, text="", font=("Arial", 25), text_color="red")
        self.errorLabel.place(relx=0.5, rely=0.85, anchor="center")

    # Handle login
    def ShowChatRoom(self):
        data = self.CheckIfFilledOut()
        if data[0]:
            self.loginFrame.pack_forget()
            self.ChatRoom(username=data[1], ip=data[2], port=data[3])
        else:
            return

    def CheckIfFilledOut(self):
        # Get all entries
        username = self.usernameEntry.get()
        ip = self.ipEntry.get()
        port = self.portEntry.get()

        # Check if all entries are filled out
        if username == "" or ip == "" or port == "":
            self.DisChanErrorMsg("All fields must be filled out")
            return [False]

        else:
            if len(username) > 25:
                self.DisChanErrorMsg("User name can't be longer than 25 characters")
                return [False]

            # Skip if username contains special characters
            if not username.isalnum():
                self.DisChanErrorMsg("User name can't contain special characters")
                return [False]

            # Check if port is a number
            if not port.isdigit():
                self.DisChanErrorMsg("Please enter a valid port")
                return [False]

            # Set username for title
            self.title(f"ChatyFy | Name: {username}")

            # If all entries are filled out and meet the correct expectations, return true
            return [True, username, ip, port]

    # Print error message in login window
    def DisChanErrorMsg(self, Emsg):
        self.errorLabel.configure(text=Emsg)

    # Chat frame
    def ChatRoom(self, username, ip, port):
        self.username = username

        # Create connection to server
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((ip, int(port)))

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, args=(self.loop,), daemon=True).start()

        asyncio.run_coroutine_threadsafe(self.connectionToServer(), self.loop)

        # Create chat frame
        self.chatframe = ctk.CTkFrame(self, width=self.windowWidth, height=self.windowHeight)
        self.chatframe.place(x=0, y=0)
        # Chat frame items
        self.chatBox = ctk.CTkScrollableFrame(self.chatframe, width=self.windowWidth//1.1, height=self.windowHeight//1.25, fg_color="black")
        self.chatBox.place(relx=0.5, rely=.425, anchor="center")
        self.enterMessage = ctk.CTkEntry(self.chatframe, width=(self.windowWidth//1.1) - 150, height=100, placeholder_text="Enter Message", bg_color="transparent", font=self.enterMessageFont, text_color="white")
        self.enterMessage.place(x=self.windowWidth-((self.windowWidth//1.1) + 75), y=self.windowHeight-125)
        self.sendMessageBtn = ctk.CTkButton(self.chatframe, text="Send", width=25, height=100, font=self.enterMessageFont, command=self.btnCommandSendMsgToServer)
        self.sendMessageBtn.place(x=self.windowWidth-175, y=self.windowHeight-125)

    def start_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def receive_message(self):
        while True:
            data = await self.loop.sock_recv(self.s, 1024)
            if not data:
                break

            # Decode the data from bytes to string
            temp = data.decode()

            try:
                # Parse the JSON string into a dictionary
                json_data = json.loads(temp)
                username = json_data.get("username")
                message = json_data.get("message")

                if username and message:
                    # Use `self.after` to safely update the GUI from the main thread
                    self.after(0, self.OtherMessages, username, message)
                else:
                    print(f"Invalid JSON data received: {json_data}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

    async def connectionToServer(self):
        await self.receive_message()

    def btnCommandSendMsgToServer(self):
        message = self.enterMessage.get()
        self.MyMessages(message)
        asyncio.run_coroutine_threadsafe(self.sendMsgToServer(message), self.loop)

    async def sendMsgToServer(self, msg):
        jsonObj = {"username": self.username, "message": msg}
        data = json.dumps(jsonObj)

        if msg == "exit();":
            self.s.close()
            exit()

        await self.loop.sock_sendall(self.s, data.encode())

    # Server communication
    def SendMsg(self):
        message = self.enterMessage.get()
        self.MyMessages(message)

    def MyMessages(self, msg: str):
        # Create message frame
        msgFrame = ctk.CTkFrame(self.chatBox, width=len(msg) * 10 + 150, height=50, fg_color="#00d4ff")
        msgFrame.pack(pady=5, padx=25, anchor='e')
        # Message label
        msgLabel = ctk.CTkLabel(msgFrame, text=msg, text_color="black", fg_color="#00d4ff")
        msgLabel.pack(padx=5, pady=5)

    def OtherMessages(self, name, msg):
        # Display name of sender of msg
        msgName = ctk.CTkLabel(self.chatBox, text=name, text_color="white")
        msgName.pack(pady=0, padx=25, anchor="w")
        # Create text box for msg
        msgFrame = ctk.CTkFrame(self.chatBox, width=len(msg) * 10 + 150, height=50, fg_color="#d3d3d3")
        msgFrame.pack(pady=0, padx=25, anchor="w")
        # Create msg label
        msgLabel = ctk.CTkLabel(msgFrame, text=msg, text_color="black", fg_color="#d3d3d3")
        msgLabel.pack(padx=5, pady=5)

class Handler():
    def __init__(self):
        pass

    def getWindowSize(self):
        for monitor in get_monitors():
            width = monitor.width
            height = monitor.height

        programm_width = width - 600
        programm_height = height - 125

        return [programm_width, programm_height]

if __name__ == '__main__':
    app = Main()
    app.mainloop()