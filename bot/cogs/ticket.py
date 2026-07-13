import discord
from discord.ui import View, Button, Select
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

# === CONSTANTES MANQUANTES ===
TICKET_CATEGORY_ID = 1525913546804826203
SUPPORT_ROLE_ID = 1525913251018178640  # ou utilise un set si plusieurs

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Buy a product", value="buy", emoji="🛒", description="Acheter un produit"),
            discord.SelectOption(label="Support for product", value="support", emoji="❓", description="Support produit")
        ]
        super().__init__(placeholder="Choisis le type de ticket...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        username = interaction.user.name.lower().replace(" ", "-")
        ticket_name = f"{ticket_type}-{username}"

        guild = interaction.guild
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)
        if not category:
            await interaction.response.send_message("❌ Catégorie de tickets non trouvée.", ephemeral=True)
            return

        # Création du channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True),
        }
        staff_role = discord.utils.get(guild.roles, id=SUPPORT_ROLE_ID)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=ticket_name,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket créé par {interaction.user}"
        )

        # Embed de bienvenue
        embed = discord.Embed(
            title="🎫 Ticket Créé",
            description=f"Bonjour {interaction.user.mention} !\nTon ticket a bien été créé.\nUn membre du staff te répondra rapidement.",
            color=0x00ff00
        )
        embed.set_footer(text="Clique sur le bouton ci-dessous pour fermer le ticket si besoin.")

        view = TicketCloseView()
        await ticket_channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ton ticket a été créé : {ticket_channel.mention}", ephemeral=True)


class OpenTicketButton(Button):
    def __init__(self):
        super().__init__(
            label="📩 Open a ticket", 
            style=discord.ButtonStyle.primary, 
            emoji="📩",
            custom_id="open_ticket_button"  # ← OBLIGATOIRE pour la persistance
        )

    async def callback(self, interaction: discord.Interaction):
        view = View()
        view.add_item(TicketSelect())
        await interaction.response.send_message("Choisis le type de ticket :", view=view, ephemeral=True)

class TicketCloseView(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistante

    @discord.ui.button(
        label="Fermer le ticket", 
        style=discord.ButtonStyle.red, 
        emoji="🔒",
        custom_id="close_ticket_button"  # ← Ajouté ici aussi
    )
    async def close(self, interaction: discord.Interaction, button: Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ Seul le staff peut fermer les tickets.", ephemeral=True)
            return
        await interaction.channel.delete(reason=f"Ticket fermé par {interaction.user}")
        logger.info(f"Ticket {interaction.channel.name} fermé par {interaction.user}")

class TicketPanel(View):
    def __init__(self):
        super().__init__(timeout=None)  # Persistante
        self.add_item(OpenTicketButton())


# === COG PRINCIPAL (nouveau) ===
class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(TicketPanel())  # Vue persistante

    @commands.command()
    async def setup_ticket(self, ctx):
        """Déploie le panneau de tickets."""
        view = TicketPanel()
        embed = discord.Embed(title="Support", description="Cliquez pour ouvrir un ticket", color=0x5865F2)
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(TicketCog(bot))
    logger.info("✅ Ticket cog chargé avec vues persistantes.")
