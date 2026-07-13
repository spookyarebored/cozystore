import discord
from discord.ui import Modal, TextInput

from bot.database.database import add_or_update_page, get_full_embed


class EditEmbedModal(Modal, title="Modifier une Page d'Embed"):
    def __init__(self, bot, embed_id: int, page_number: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.embed_id = embed_id
        self.page_number = page_number
        
        self.title_input = TextInput(label="Titre", required=True)
        self.desc_input = TextInput(label="Description", style=discord.TextStyle.paragraph, required=True)
        self.footer_input = TextInput(label="Footer", required=False)
        
        self.add_item(self.title_input)
        self.add_item(self.desc_input)
        self.add_item(self.footer_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        page_data = {
            "title": self.title_input.value,
            "description": self.desc_input.value,
            "footer": self.footer_input.value or None
        }
        await add_or_update_page(self.embed_id, self.page_number, page_data)
        await interaction.followup.send("✅ Page modifiée avec succès !", ephemeral=True)
