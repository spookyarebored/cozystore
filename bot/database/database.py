import aiosqlite
import discord
from pathlib import Path
from typing import List

from config import config
import logging

logger = logging.getLogger(__name__)

DB_PATH = config.DB_PATH

async def init_db():
    Path("data").mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS EmbedGroups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS EmbedMessages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                title TEXT,
                description TEXT NOT NULL,
                color INTEGER DEFAULT 0x5865F2,
                footer TEXT DEFAULT 'Dev by astrieontheplace',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES EmbedGroups(id) ON DELETE CASCADE
            )
        """)
        await db.commit()
        print("✅ DB chargée.")

async def create_group(guild_id: int, name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("INSERT INTO EmbedGroups (guild_id, name) VALUES (?, ?) RETURNING id", (guild_id, name)) as cursor:
            row = await cursor.fetchone()
        await db.commit()
        return row[0]

async def get_all_groups(guild_id: int) -> List[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id, name FROM EmbedGroups WHERE guild_id = ? ORDER BY created_at DESC", (guild_id,)) as cursor:
            rows = await cursor.fetchall()
            return [{"id": row[0], "name": row[1]} for row in rows]

async def delete_group(guild_id: int, name: str) -> bool:
    """Supprime un groupe et tous ses embeds associés."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "DELETE FROM EmbedGroups WHERE guild_id = ? AND name = ?", 
            (guild_id, name)
        ) as cursor:
            deleted = cursor.rowcount > 0
        await db.commit()
        
        if deleted:
            logger.info(f"Groupe supprimé: {name} (guild {guild_id})")
        return deleted

async def add_embed_to_group(group_name: str, guild_id: int, embed_name: str, title: str, description: str, color: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id FROM EmbedGroups WHERE name = ? AND guild_id = ?", (group_name, guild_id)) as cursor:
            group_row = await cursor.fetchone()
            if not group_row:
                raise ValueError("Groupe non trouvé")
            group_id = group_row[0]
        await db.execute("""
            INSERT INTO EmbedMessages (group_id, guild_id, name, title, description, color, footer)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (group_id, guild_id, embed_name, title, description, color, "Dev by astrieontheplace"))
        await db.commit()

async def get_group_embeds(group_name: str, guild_id: int) -> List[discord.Embed]:
    embeds = []
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT title, description, color, footer
            FROM EmbedMessages 
            JOIN EmbedGroups ON EmbedMessages.group_id = EmbedGroups.id
            WHERE EmbedGroups.name = ? AND EmbedGroups.guild_id = ?
            ORDER BY EmbedMessages.created_at
        """, (group_name, guild_id)) as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                embed = discord.Embed(title=row[0] or "Sans titre", description=row[1], color=row[2] or 0x5865F2)
                embed.set_footer(text=row[3] or "Dev by astrieontheplace")
                embeds.append(embed)
    return embeds
