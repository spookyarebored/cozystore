import discord
from discord import app_commands
from discord.ext import commands

from bot.database.database import create_group, create_embed_in_group

class EmbedManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="group-create", description="Créer un groupe d'embeds (dossier)")
    @app_commands.default_permissions(administrator=True)
    async def group_create(self, interaction: discord.Interaction, name: str):
        try:
            await create_group(interaction.guild_id, name)
            await interaction.response.send_message(f"✅ Groupe '{name}' créé avec succès !", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message("Erreur lors de la création du groupe.", ephemeral=True)

    # Ajoute les autres commandes comme avant

async def setup(bot):
    await bot.add_cog(EmbedManager(bot))
