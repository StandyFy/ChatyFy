import customtkinter as ctk
from screeninfo import get_monitors
import socket
import asyncio
import json
import threading
import winreg
from win10toast import ToastNotifier as TN
import os
import configparser

class Style():
    def __init__(self):
        pass

    def setTheme(self, theme):
        if theme == 'light':
           color = {
                'main_bg': '#dcdcdc',
                'frame_fg': '#ffffff',
                'font_color': '#000000',
                'login_entry_fg': '#dcdcdc',
                'placeolder_color': '#7b7b7b',
                'login_btn_bg': '#000000',
                'login_btn_fg': '#0080d8',
                'login_btn_hover': '#006ab3',
                'transparent': 'transparent',
                'usernameColor': "#000000",
                "error_msg": "#ff0000"
            }
           
        if theme == 'dark':
            color = {
                'main_bg': '#363636',
                'frame_fg': '#000000',
                'font_color': '#ffffff',
                'login_entry_fg': '#363636',
                'placeolder_color': '#7b7b7b',
                'login_btn_bg': '#000000',
                'login_btn_fg': '#0080d8',
                'login_btn_hover': '#006ab3',
                'transparent': 'transparent',
                'usernameColor': "#ffffff",
                "error_msg": "#ff0000"
            }

        if theme == 'unknown':
            print("Unknown theme")
            input("Press enter to exit")
            quit()
            exit()


        if self.isJson(color):
            return json.dumps(color)

        else: 
            return color
        
    def GetSysTheme(self):
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')

        try:
            theme_val = winreg.QueryValueEx(key, 'AppsUseLightTheme')[0]
            return 'light' if theme_val == 1 else 'dark'
        except FileNotFoundError:
            return 'unknown'

    def isJson(self, json_obj):
        try:
            return True
        except ValueError as e:
            return False

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
        window_size = self.handler.getWindowSize()
        self.windowWidth = window_size[0]
        self.windowHeight = window_size[1]

        # Set up default window
        self.title(titleText)
        self.geometry(f"{self.windowWidth}x{self.windowHeight}")
        self.resizable(0, 0)

        # Set Styles
        styleClass = Style()
        style = styleClass.setTheme(styleClass.GetSysTheme())
        self.style = json.loads(style)

        self.DisplayLogin()

    # Login frame
    def DisplayLogin(self):
        # Create login frame
        self.loginFrame = ctk.CTkFrame(self, width=self.windowWidth, height=self.windowHeight, fg_color=self.style['main_bg'], bg_color=self.style['main_bg'])
        self.loginFrame.place(x=0, y=0)
        # Login frame items
        # Login background
        self.loginBG = ctk.CTkFrame(self.loginFrame, width=self.windowWidth//2, height=self.windowHeight*0.65, fg_color=self.style['frame_fg'], corner_radius=15)
        self.loginBG.place(relx=0.5, rely=0.5, anchor="center")
        # Login header
        self.header = ctk.CTkLabel(self.loginBG, text="Login to local chatroom", font=("Arial", 50), fg_color=self.style['frame_fg'], text_color=self.style['font_color'])
        self.header.place(relx=0.5, rely=0.1, anchor="center")
        # Username entry
        self.usernameEntry = ctk.CTkEntry(self.loginBG, width=250, height=50, placeholder_text="Username", font=("Arial", 25), bg_color=self.style['transparent'], text_color=self.style['font_color'], fg_color=self.style['login_entry_fg'], placeholder_text_color=self.style['placeolder_color'])
        self.usernameEntry.place(relx=0.5, rely=0.25, anchor="center")
        # IP entry
        self.ipEntry = ctk.CTkEntry(self.loginBG, width=250, height=50, placeholder_text="IP Address", font=("Arial", 25), bg_color=self.style['transparent'], text_color=self.style['font_color'], fg_color=self.style['login_entry_fg'], placeholder_text_color=self.style['placeolder_color'])
        self.ipEntry.place(relx=0.5, rely=0.40, anchor="center")
        # Port entry
        self.portEntry = ctk.CTkEntry(self.loginBG, width=250, height=50, placeholder_text="Port", font=("Arial", 25), bg_color=self.style['transparent'], text_color=self.style['font_color'], fg_color=self.style['login_entry_fg'], placeholder_text_color=self.style['placeolder_color'])
        self.portEntry.place(relx=0.5, rely=0.55, anchor="center")
        # Login button
        self.loginBtn = ctk.CTkButton(self.loginBG, text="Login", width=250, height=50, font=("Arial", 25), command=self.ShowChatRoom, fg_color=self.style['login_btn_fg'], text_color=self.style['font_color'], hover_color=self.style['login_btn_hover'])
        self.loginBtn.place(relx=0.5, rely=0.70, anchor="center")

        # Error messages
        self.errorLabel = ctk.CTkLabel(self.loginBG, text="", font=("Arial", 25), text_color=self.style['error_msg'])
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
        self.chatframe = ctk.CTkFrame(self, width=self.windowWidth, height=self.windowHeight, fg_color=self.style['main_bg'], bg_color=self.style['main_bg'])
        self.chatframe.place(x=0, y=0)
        # Chat frame items
        self.chatBox = ctk.CTkScrollableFrame(self.chatframe, width=self.windowWidth//1.1, height=self.windowHeight//1.25, fg_color=self.style['frame_fg'])
        self.chatBox.place(relx=0.5, rely=.425, anchor="center")
        self.enterMessage = ctk.CTkEntry(self.chatframe, width=(self.windowWidth//1.1) - 150, height=100, placeholder_text="Enter Message", bg_color=self.style['transparent'], font=self.enterMessageFont, text_color=self.style['font_color'], fg_color=self.style['login_entry_fg'], placeholder_text_color=self.style['placeolder_color'])
        self.enterMessage.place(x=self.windowWidth-((self.windowWidth//1.1) + 75), y=self.windowHeight-125)
        self.sendMessageBtn = ctk.CTkButton(self.chatframe, text="Send", width=25, height=100, font=self.enterMessageFont, command=self.btnCommandSendMsgToServer, fg_color=self.style['login_btn_fg'], text_color=self.style['font_color'], )
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

        # Check if message is empty and dont send
        if message == "" or message.isspace() or message == None:
            return

        # Clear message box
        self.enterMessage.delete(0, 'end')

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
        msgName = ctk.CTkLabel(self.chatBox, text=name, text_color=self.style["usernameColor"], fg_color=self.style['transparent'])
        msgName.pack(pady=0, padx=25, anchor="w")
        # Create text box for msg
        msgFrame = ctk.CTkFrame(self.chatBox, width=len(msg) * 10 + 150, height=50, fg_color="#d3d3d3")
        msgFrame.pack(pady=0, padx=25, anchor="w")
        # Create msg label
        msgLabel = ctk.CTkLabel(msgFrame, text=msg, text_color="black", fg_color="#d3d3d3")
        msgLabel.pack(padx=5, pady=5)

        #check if user has notifications enabled
        cp = configparser.ConfigParser()
        cp.read(os.path.dirname(os.path.abspath(__file__)) + '\\config.ini')
        if cp.getboolean("chatapp", "notifications") == True:
            # Notify user if window is not focus
            handler = Handler()
            if(self.focus_get() is None):
                handler.notification(username=name)



class Handler():
    def __init__(self):
        pass

    def getWindowSize(self):
        for monitor in get_monitors():
            if monitor.is_primary:
                print(monitor)
                width:int = monitor.width * 0.75  # WTF THIS IS CURSED AS HELL
                height = monitor.height * 0.90

        return [int(width), int(height)]
    
    def notification(self, username:str = "N/A"):
        currentDir = os.path.dirname(os.path.abspath(__file__))

        toast = TN()
        toast.show_toast(
            "ChatyFy",
            f"You have a new message from: {username}",
            duration=15,
            icon_path= currentDir + "\\resources\\ChatyFyLogo.ico",
            threaded=True
        )

if __name__ == '__main__':
    app = Main()
    app.mainloop()