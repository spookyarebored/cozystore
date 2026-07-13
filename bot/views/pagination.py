import discord
from discord.ui import View, Button

class EmbedPaginator(View):
    def __init__(self, embeds: list[discord.Embed]):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.current = 0
        self._update_buttons()

    def _update_buttons(self):
        self.previous.disabled = (self.current == 0)
        self.next.disabled = (self.current == len(self.embeds) - 1)

    @discord.ui.button(label="◀️", style=discord.ButtonStyle.gray)
    async def previous(self, interaction: discord.Interaction, button: Button):
        self.current = max(0, self.current - 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)

    @discord.ui.button(label="▶️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: Button):
        self.current = min(len(self.embeds) - 1, self.current + 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current], view=self)
