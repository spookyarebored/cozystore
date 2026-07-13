import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    APPLICATION_ID: int = int(os.getenv("APPLICATION_ID", "0") or 0)
    DB_PATH: str = "data/database.sqlite"

config = Config()

if not config.TOKEN:
    raise ValueError("DISCORD_TOKEN manquant dans .env")
