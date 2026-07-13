import discord
from discord.ui import View

class GroupEmbedView(View):
    def __init__(self, embeds_list):
        super().__init__()
        self.embeds_list = embeds_list
        self.current = 0

    @discord.ui.button(label="⬅️")
    async def previous(self, interaction, button):
        self.current = max(0, self.current - 1)
        await self.update(interaction)

    @discord.ui.button(label="➡️")
    async def next(self, interaction, button):
        self.current = min(len(self.embeds_list) - 1, self.current + 1)
        await self.update(interaction)

    async def update(self, interaction):
        await interaction.response.edit_message(embed=self.embeds_list[self.current], view=self)
