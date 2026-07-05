if __name__ == "__main__":
    import os
    import shutil
    from sys import argv

    if argv[1] == "--server":
        from PyInstaller.__main__ import run as pyinstaller

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

    elif argv[1] == "--client":
        from PyInstaller.__main__ import run as pyinstaller

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
    exit()
