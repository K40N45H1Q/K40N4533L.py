from aiogram import Bot
from dataclasses import dataclass

@dataclass
class Config:
    port: int = 3301
    host: str = "0.0.0.0"
    chat_id: int = 8810484379
    token: str = "8828822456:AAEuFpjZiiv0ocGFoAiqGfHXGlj0dm-n67Y"
    url: str | None = None
    visibility = 0

    def __post_init__(self):
        self.bot = Bot(self.token)