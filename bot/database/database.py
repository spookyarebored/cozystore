import aiosqlite
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from config import config

DB_PATH = config.DB_PATH

async def init_db():
    Path("data").mkdir(exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        # Groupes (dossiers)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS EmbedGroups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Embeds dans les groupes
        await db.execute("""
            CREATE TABLE IF NOT EXISTS EmbedMessages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER,
                guild_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Pages
        await db.execute("""
            CREATE TABLE IF NOT EXISTS EmbedPages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                embed_id INTEGER NOT NULL,
                page_number INTEGER NOT NULL,
                title TEXT,
                description TEXT NOT NULL,
                color INTEGER DEFAULT 0x5865F2,
                thumbnail TEXT,
                image TEXT,
                footer TEXT,
                fields TEXT DEFAULT '[]',
                FOREIGN KEY (embed_id) REFERENCES EmbedMessages(id) ON DELETE CASCADE
            )
        """)
        await db.commit()

async def create_group(guild_id: int, name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("INSERT INTO EmbedGroups (guild_id, name) VALUES (?, ?) RETURNING id", (guild_id, name)) as cursor:
            row = await cursor.fetchone()
        await db.commit()
        return row[0]

async def create_embed_in_group(group_id: int, guild_id: int, name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("INSERT INTO EmbedMessages (group_id, guild_id, name) VALUES (?, ?, ?) RETURNING id", (group_id, guild_id, name)) as cursor:
            row = await cursor.fetchone()
        await db.commit()
        return row[0]

async def add_page_to_embed(embed_id: int, page_number: int, page_data: Dict[str, Any]):
    fields_json = json.dumps(page_data.get("fields", []))
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO EmbedPages (embed_id, page_number, title, description, color, thumbnail, image, footer, fields)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (embed_id, page_number, page_data.get("title"), page_data.get("description"), page_data.get("color"), page_data.get("thumbnail"), page_data.get("image"), page_data.get("footer"), fields_json))
        await db.commit()

async def get_group_embeds(group_name: str, guild_id: int) -> List[Dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT id FROM EmbedGroups WHERE name = ? AND guild_id = ?", (group_name, guild_id)) as cursor:
            group_row = await cursor.fetchone()
            if not group_row:
                return []
            group_id = group_row[0]
        # Récupérer tous les embeds du groupe
        # Logique complète dans le cog
        return []
