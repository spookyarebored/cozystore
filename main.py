import asyncio
import logging
from pathlib import Path

import discord
from discord.ext import commands

import sys
sys.path.insert(0, str(Path(__file__).parent))

from bot.database.database import init_db
from config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmbedBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, application_id=config.APPLICATION_ID)

    async def setup_hook(self):
        await init_db()
        await self.load_extension("bot.cogs.embed_manager")
        try:
            await asyncio.wait_for(self.tree.sync(), timeout=15)
            logger.info("✅ Sync terminé.")
        except Exception as e:
            logger.warning(f"Sync warning: {e}")

    async def on_ready(self):
        logger.info(f"✅ {self.user} connecté !")

bot = EmbedBot()

async def main():
    async with bot:
        await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
