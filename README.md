# This is a chat app written in Python.

You can compile it yourself using the `CX_Freeze` library to create an .exe.

I had a lot of fun and pain working on this project.
If you have any tipps or want to add extras please do so and let me know.

## How to use
### **Step 1:**
Run `server.py`, then enter an `IP address` or use `localhost` and enter a `port` where the server should listen.

### **Step 2**:
Now the user can start the client software and enter a `username`, `IP address`, and `port`.
The client will then try to connect to the server. If it succeeds, the chat overlay will be shown, and messages can be sent.

### **Disclaimer**
Remember, this is an **unmoderated** chat space with **no language filters or other protections**. 


## How to compile
### **Step 1**:
Make sure to install all librarys:
`customtkinter`
`screeninfo`
`socket`
`asyncio`
`json`
`threading`
`cx_Freeze`

## **Step 2:**
Open your terminal and navigate to the `server.py`

## **Step 3:**
Run following command: `python setup.py build`

## **Step 4:**
Now you have an new folder where you find the `.exe`
