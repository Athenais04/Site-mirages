import discord
from discord.ext import commands, tasks
from discord import app_commands
from database import get_balance, get_top_users, get_shop_items
import asyncio
import sqlite3  # ou autre méthode pour accéder aux données

GUILD_ID = 1382310288115761215  # Remplace par ton ID de serveur
CHANNEL_ID = 1382315923427295275  # Remplace par l'ID du salon où afficher le menu

# Exemple de fonctions de récupération de données
def get_balance(user_id):
    return 1200  # Simule une balance

def get_top_users(limit=3):
    return [(123, 2400), (456, 1800), (789, 1500)]  # Simule le top 3

def get_inventory(user_id):
    return ["🎁 Pack Bonus", "💎 Gemme rare"]  # Simule un inventaire

def get_shop_items():
    return ["🔥 Boost XP", "📦 Pack Mystère", "🎫 Ticket VIP"]  # Simule la boutique


class BoostHelpSelect(discord.ui.Select):
    def __init__(self, view):
        options = [
            discord.SelectOption(label="Solde & Classement", value="balance", emoji="💰"),
            discord.SelectOption(label="Boutique", value="shop", emoji="🛍️"),
            discord.SelectOption(label="Jeux de casino", value="casino", emoji="🎰"),
            discord.SelectOption(label="Commandes Admin", value="admin", emoji="🛠️"),
        ]
        super().__init__(placeholder="📂 Choisis une catégorie...", options=options)
        self.view = view

        async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        embed = discord.Embed(color=discord.Color.blurple())

        if choice == "balance":
            coins = get_balance(interaction.user.id)
            top_users = get_top_users()

            top_text = ""
            for i, (uid, coins_amt) in enumerate(top_users, start=1):
                user = interaction.guild.get_member(uid)
                name = user.display_name if user else f"<@{uid}>"
                top_text += f"**#{i}** {name} — {coins_amt} 💰\n"

            embed.title = "💰 Solde & Classement"
            embed.description = (
                f"**Ton solde :** {coins} BoostCoins\n\n"
                f"**Top 3 des plus riches :**\n{top_text}"
            )

        elif choice == "shop":
            items = get_shop_items()
            embed.title = "🛍️ Boutique"
            embed.description = "\n".join(
                f"• **{name}** — {price}💰\n> {desc}" for name, desc, price in items
            ) or "La boutique est vide pour le moment."

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
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self.select = BoostHelpSelect(self)
        self.add_item(self.select)

    async def update_embed(self, interaction: discord.Interaction, choice: str):
        embed = discord.Embed(color=discord.Color.blurple())

        if choice == "balance":
            balance = get_balance(interaction.user.id)
            top = get_top_users()
            embed.title = "💰 Solde & Classement"
            embed.description = (
                f"**Ton solde :** `{balance} BoostCoins`\n\n"
                "**🏆 Top 3 :**\n" +
                "\n".join([f"<@{uid}> — `{coins} 💰`" for uid, coins in top])
            )

        elif choice == "shop":
            inventory = get_inventory(interaction.user.id)
            items = get_shop_items()
            embed.title = "🛍️ Boutique"
            embed.add_field(name="🧾 Inventaire", value="\n".join(inventory) or "Aucun objet", inline=True)
            embed.add_field(name="🛒 Objets disponibles", value="\n".join(items), inline=True)

        elif choice == "casino":
            embed.title = "🎰 Jeux de casino"
            embed.description = (
                "`/roulette` — Parie sur un numéro ou une couleur\n"
                "`/dice` — Lance les dés contre le bot\n"
                "`/slot` — Tire la manette !"
            )

        elif choice == "admin":
            embed.title = "🛠️ Commandes Admin"
            embed.description = (
                "`/addcoins @membre montant`\n"
                "`/removecoins @membre montant`\n"
                "`/edititem id champ valeur`\n"
                "`/postshop`"
            )

        await interaction.response.edit_message(embed=embed, view=self)


class BoostCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_task.start()

    def cog_unload(self):
        self.persistent_task.cancel()

    @tasks.loop(count=1)
    async def persistent_task(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(GUILD_ID)
        channel = guild.get_channel(CHANNEL_ID)
        if channel:
            embed = discord.Embed(
                title="📘 Menu BoostCoins",
                description="Choisis une catégorie ci-dessous pour voir les infos.",
                color=discord.Color.blurple()
            )
            view = BoostHelpView(user=self.bot.user)
            await channel.send(embed=embed, view=view)

    @app_commands.command(name="boost", description="Affiche le menu BoostCoins")
    async def boost(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 Menu BoostCoins",
            description="Choisis une catégorie ci-dessous pour voir les infos.",
            color=discord.Color.blurple()
        )
        view = BoostHelpView(user=interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(BoostCommands(bot))
