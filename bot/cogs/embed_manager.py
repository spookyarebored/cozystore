import discord
import logging
from discord import app_commands, ui
from discord.ext import commands

from bot.database.database import create_group, get_all_groups, add_embed_to_group, get_group_embeds
from bot.views.pagination import EmbedPaginator

logger = logging.getLogger(__name__)

PRICE_ROLE_ID = 1525913263550759032
ALL_COMMANDE_ROLE_ID = 1525913251018178640
TICKET_CHANNEL_ID = 1525913302352531456

class EmbedManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def group_autocomplete(self, interaction: discord.Interaction, current: str):
        groups = await get_all_groups(interaction.guild_id)
        choices = [app_commands.Choice(name=g['name'], value=g['name']) for g in groups if current.lower() in g['name'].lower()][:25]
        return choices

    def has_allowed_role(self, interaction: discord.Interaction) -> bool:
        return any(role.id == PRICE_ROLE_ID for role in interaction.user.roles)
    
    def has_allowed_owner_role(self, interaction: discord.Interaction) -> bool:
        return any(role.id == ALL_COMMANDE_ROLE_ID for role in interaction.user.roles)

    @app_commands.command(name="groupe-create", description="Créer un groupe")
    async def groupe_create(self, interaction: discord.Interaction, name: str):
        if not self.has_allowed_owner_role(interaction):
            await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
            return
        try:
            await create_group(interaction.guild_id, name)
            await interaction.response.send_message(f"✅ Groupe **{name}** créé !", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur: {e}")
            await interaction.response.send_message("❌ Erreur.", ephemeral=True)

    @app_commands.command(name="groupe-list", description="Lister les groupes")
    async def groupe_list(self, interaction: discord.Interaction):
        if not self.has_allowed_owner_role(interaction):
            await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
            return
        try:
            groups = await get_all_groups(interaction.guild_id)
            if not groups:
                await interaction.response.send_message("📭 Aucun groupe.", ephemeral=True)
                return
            embed = discord.Embed(title="📋 Groupes", color=0x5865F2)
            for g in groups:
                embed.add_field(name=g['name'], value=f"ID: {g['id']}", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur: {e}")
            await interaction.response.send_message("❌ Erreur.", ephemeral=True)

    @app_commands.command(name="embed-create", description="Créer un embed")
    @app_commands.autocomplete(group_name=group_autocomplete)
    async def embed_create(self, interaction: discord.Interaction, group_name: str, embed_name: str):
        if not self.has_allowed_owner_role(interaction):
            await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
            return
        try:
            groups = await get_all_groups(interaction.guild_id)
            if not any(g['name'].lower() == group_name.lower() for g in groups):
                await interaction.response.send_message("❌ Groupe inexistant.", ephemeral=True)
                return
            await interaction.response.send_modal(EmbedCreationModal(self, group_name, embed_name))
        except Exception as e:
            logger.error(f"Erreur: {e}")
            await interaction.response.send_message("❌ Erreur.", ephemeral=True)

    @app_commands.command(name="price", description="Voir les prix du groupe selectionné")
    @app_commands.autocomplete(group_name=group_autocomplete)
    async def price(self, interaction: discord.Interaction, group_name: str):
        if not (self.has_allowed_role(interaction) or self.has_allowed_owner_role(interaction)):
            await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
            return
        try:
            embeds = await get_group_embeds(group_name, interaction.guild_id)
            if not embeds:
                await interaction.response.send_message("❌ Aucun embed.", ephemeral=True)
                return
            view = EmbedPaginator(embeds)
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur: {e}")
            await interaction.response.send_message("❌ Erreur.", ephemeral=True)

class EmbedCreationModal(ui.Modal, title="Créer un Embed"):
    title_input = ui.TextInput(label="Titre", required=True)
    description_input = ui.TextInput(label="Description", style=discord.TextStyle.paragraph, required=True)
    color_input = ui.TextInput(label="Couleur hex", placeholder="5865F2", required=False)

    def __init__(self, cog, group_name: str, embed_name: str):
        super().__init__()
        self.cog = cog
        self.group_name = group_name
        self.embed_name = embed_name

    async def on_submit(self, interaction: discord.Interaction):
        if not any(role.id == ALL_COMMANDE_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
            return
        try:
            color = int(self.color_input.value or "5865F2", 16)
            full_description = self.description_input.value + f"\n\n📩 **Open Ticket** : <#{TICKET_CHANNEL_ID}>"
            await add_embed_to_group(self.group_name, interaction.guild_id, self.embed_name, self.title_input.value, full_description, color)
            embed = discord.Embed(title=self.title_input.value, description=full_description, color=color)
            embed.set_footer(text="Dev by astrieontheplace")
            await interaction.response.send_message(embed=embed, content=f"✅ Embed sauvegardé !", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur: {e}")
            await interaction.response.send_message("❌ Erreur.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(EmbedManager(bot))
    logger.info("✅ Bot complet chargé.")
