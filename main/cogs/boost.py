import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class BoostHelpSelect(discord.ui.Select):
    def __init__(self, parent_view):
        options = [
            discord.SelectOption(label="Solde & Classement", description="Voir tes BoostCoins", emoji="💰", value="balance"),
            discord.SelectOption(label="Boutique", description="Acheter des objets", emoji="🛍️", value="shop"),
            discord.SelectOption(label="Jeux de casino", description="Roulette, dés, slot", emoji="🎰", value="casino"),
            discord.SelectOption(label="Commandes Admin", description="Gestion et modération", emoji="🛠️", value="admin"),
        ]
        super().__init__(placeholder="Choisis une catégorie d'aide...", min_values=1, max_values=1, options=options)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        embed = discord.Embed(color=discord.Color.blurple())

        if choice == "balance":
            embed.title = "💰 Solde & Classement"
            embed.description = (
                "`/balance` — Affiche ton solde de BoostCoins\n"
                "`/balance @membre` — Solde d'un autre membre\n"
                "`/topcoins` — Classement des plus riches"
            )
        elif choice == "shop":
            embed.title = "🛍️ Boutique"
            embed.description = (
                "`/shop` — Affiche la boutique interactive\n"
                "`/catalogue` — Voir tous les objets disponibles\n"
                "`/inventory` — Voir tes objets achetés"
            )
        elif choice == "casino":
            embed.title = "🎰 Jeux de casino"
            embed.description = (
                "`/roulette` — Jouer à la roulette\n"
                "`/dice` — Jeu de dés\n"
                "`/slot` — Machine à sous"
            )
        elif choice == "admin":
            embed.title = "🛠️ Commandes Admin"
            embed.description = (
                "`/addcoins @membre montant` — Ajouter des BoostCoins\n"
                "`/removecoins @membre montant` — Retirer des BoostCoins\n"
                "`/edititem <id> champ valeur` — Modifier un article\n"
                "`/postshop` — Poster le message permanent boutique"
            )
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

class BoostHelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.select = BoostHelpSelect(self)
        self.add_item(self.select)
        self.message = None

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

class BoostCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="boost", description="Affiche l'aide pour les commandes BoostCoins")
    async def boost(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 Aide BoostCoins",
            description="Choisis une catégorie dans le menu déroulant ci-dessous pour voir les commandes.",
            color=discord.Color.blurple()
        )
        view = BoostHelpView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        # Petit délai pour que le message soit bien envoyé
        await asynci
