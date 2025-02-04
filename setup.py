from cx_Freeze import setup, Executable

setup(
    name="ChatyFy",
    version="1.0",
    description="A self written Chat Client in Python",
    executables=[Executable("client.py", base="gui")],
)