"""
Configuration corrigée - compatible dataclass frozen.
"""
import os
from dataclasses import dataclass, field
from typing import Final

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    TOKEN: Final[str] = os.getenv("DISCORD_TOKEN", "")
    DB_PATH: Final[str] = "data/database.sqlite"
    APPLICATION_ID: Final[int | None] = int(os.getenv("APPLICATION_ID", "0")) or None
    OWNER_IDS: Final[list[int]] = field(default_factory=list)
    BOT_NAME: Final[str] = "CozyStore Embed Bot"


config = Config()


if not config.TOKEN:
    raise ValueError("❌ DISCORD_TOKEN non défini dans .env")