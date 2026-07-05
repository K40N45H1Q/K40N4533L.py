from sys import argv
from asyncio import run
from websockets import connect
try: from src.config import Config
except ImportError: from config import Config


class Client(Config):
    def __init__(self):
        super().__init__()
        self.url = argv[2].replace("https://", "wss://")

    async def run(self):
        async with connect(self.url) as websocket:
            while True:
                command = input("[Shell] > ").strip()

                if command in ["exit", "quit"]:
                    return

                if command in ("cls", "clear"):
                    print("\x1b[2J\x1b[H", end="")
                    continue

                if not command:
                    continue

                await websocket.send(command)
                print(await websocket.recv())


if __name__ == "__main__":
    run(Client().run())
