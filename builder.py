import os
import shutil
from sys import argv
from PyInstaller.__main__ import run as pyinstaller


def build_server():
    pyinstaller([
        "--onefile",
        "--icon", "hot.ico",
         "--name", "server",
        "src/server.py"
    ])
    shutil.move("dist/server.exe", "server.exe")
    if os.path.isdir("dist"):
        shutil.rmtree("dist")
    if os.path.isdir("build"):
        shutil.rmtree("build")
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)


def build_client():
    pyinstaller([
        "--onefile",
        "--icon", "hot.ico",
        "--name", "client",
        "src/client.py"
    ])
    shutil.move("dist/client.exe", "client.exe")
    if os.path.isdir("dist"):
        shutil.rmtree("dist")
    if os.path.isdir("build"):
        shutil.rmtree("build")
    for f in os.listdir("."):
        if f.endswith(".spec"):
            os.remove(f)


if __name__ == "__main__":
    build_server()
    build_client()