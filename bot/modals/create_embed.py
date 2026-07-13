import discord
from discord.ui import Modal, TextInput

from bot.database.database import create_embed_message, add_or_update_page


class CreateEmbedModal(Modal, title="Créer un Embed Paginé"):
    def __init__(self, bot, name: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.name = name
        
        self.title_input = TextInput(label="Titre de la page 1", placeholder="Bienvenue sur le serveur", required=True, max_length=256)
        self.desc_input = TextInput(label="Description", style=discord.TextStyle.paragraph, placeholder="Contenu de la page...", required=True, max_length=4000)
        self.footer_input = TextInput(label="Footer (optionnel)", required=False)
        
        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.footer_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed_id = await create_embed_message(interaction.guild_id, interaction.channel_id, self.name)
        
        page_data = {
            "title": self.title_input.value,
            "description": self.desc_input.value,
            "footer": self.footer_input.value or None,
            "color": 0x5865F2
        }
        await add_or_update_page(embed_id, 1, page_data)
        await interaction.followup.send(f"✅ Embed **{self.name}** créé avec succès !\nUtilise `/embed-send {self.name}` pour l'envoyer.", ephemeral=True)
