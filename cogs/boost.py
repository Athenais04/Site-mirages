import discord
from discord.ext import commands, tasks
from discord import app_commands
from database import get_balance, get_top_users, get_inventory, get_shop_items

GUILD_ID = 1382310288115761215
CHANNEL_ID = 1382315923427295275

# ========================== MENU MEMBRE ==========================

class MemberMenuSelect(discord.ui.Select):
    def __init__(self, parent_view):
        options = [
            discord.SelectOption(label="Solde & Classement", value="balance", emoji="💰"),
            discord.SelectOption(label="Inventaire", value="inventory", emoji="🎒"),
            discord.SelectOption(label="Casino", value="casino", emoji="🎰"),
            discord.SelectOption(label="Boutique", value="shop", emoji="🛍️"),
        ]
        super().__init__(placeholder="📂 Choisis une section...", options=options)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        await self.parent_view.update_embed(interaction, self.values[0])

class MemberMenuView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self.select = MemberMenuSelect(self)
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

        elif choice == "inventory":
            inventory = get_inventory(interaction.user.id)
            embed.title = "🎒 Inventaire"
            embed.description = "\n".join(inventory) if inventory else "Aucun objet dans ton inventaire."

        elif choice == "casino":
            embed.title = "🎰 Casino"
            embed.description = (
                "`/roulette` — Parie sur un numéro ou une couleur\n"
                "`/dice` — Lance les dés contre le bot\n"
                "`/blackjack` — Joue contre la banque"
            )

        elif choice == "shop":
            items = get_shop_items()
            embed.title = "🛍️ Boutique"
            for name, desc, price in items:
                embed.add_field(name=f"{name} — {price} 💰", value=desc, inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

# ========================== MENU STAFF ==========================

class AdminMenuSelect(discord.ui.Select):
    def __init__(self, parent_view):
        options = [
            discord.SelectOption(label="Gestion BoostCoins", value="coins", emoji="🪙"),
            discord.SelectOption(label="Gestion Boutique", value="shop", emoji="🛍️"),
            discord.SelectOption(label="Gestion des Inventaires", value="inventory", emoji="🎒"),
        ]
        super().__init__(placeholder="🛠️ Menu staff : choisis une section", options=options)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        await self.parent_view.update_embed(interaction, self.values[0])

class AdminMenuView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self.select = AdminMenuSelect(self)
        self.add_item(self.select)

    async def update_embed(self, interaction: discord.Interaction, choice: str):
        embed = discord.Embed(color=discord.Color.gold())

        if choice == "coins":
            embed.title = "🪙 Gestion BoostCoins"
            embed.description = (
                "`/addcoins @membre montant` — Ajouter des BoostCoins\n"
                "`/removecoins @membre montant` — Retirer des BoostCoins"
            )

        elif choice == "shop":
            embed.title = "🛍️ Gestion Boutique"
            embed.description = (
                "`/edititem` — Modifier un item (prix, stock)\n"
                "`/additem` — Ajouter un objet à la boutique\n"
                "`/removeitem` — Supprimer un objet"
            )

        elif choice == "inventory":
            embed.title = "🎒 Gestion des Inventaires"
            embed.description = (
                "`/additemto @membre objet` — Ajouter un objet à l’inventaire\n"
                "`/removeitemfrom @membre objet` — Retirer un objet"
            )

        await interaction.response.edit_message(embed=embed, view=self)

# ========================== COG ==========================

class BoostCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.post_menu_once.start()

    def cog_unload(self):
        self.post_menu_once.cancel()

    @tasks.loop(count=1)
    async def post_menu_once(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(GUILD_ID)
        channel = guild.get_channel(CHANNEL_ID)
        if not guild or not channel:
            print("❌ Serveur ou salon introuvable.")
            return

        # Menu Membre
        embed = discord.Embed(
            title="📘 Menu BoostCoins",
            description="Choisis une section dans le menu déroulant ci-dessous pour voir tes infos.",
            color=discord.Color.blurple()
        )
        view = MemberMenuView(user=self.bot.user)
        await channel.send(embed=embed, view=view)

        # Menu Staff : visible uniquement si le rôle "staff" existe
        staff_role = discord.utils.get(guild.roles, name="staff")
        if staff_role:
            embed_admin = discord.Embed(
                title="🛠️ Menu Staff BoostCoins",
                description="Outils de gestion BoostCoins accessibles au staff.",
                color=discord.Color.gold()
            )
            admin_view = AdminMenuView(user=self.bot.user)
            await channel.send(embed=embed_admin, view=admin_view)
        else:
            print("⚠️ Rôle 'staff' non trouvé sur le serveur.")

    @app_commands.command(name="postmenu", description="Affiche le menu BoostCoins adapté à ton rôle")
    async def postmenu(self, interaction: discord.Interaction):
        roles = [r.name.lower() for r in interaction.user.roles]
        if "staff" in roles:
            view = AdminMenuView(user=interaction.user)
            embed = discord.Embed(
                title="🛠️ Menu Administration BoostCoins",
                description="Outils de gestion BoostCoins accessibles au staff.",
                color=discord.Color.gold()
            )
        elif "membre" in roles:
            view = MemberMenuView(user=interaction.user)
            embed = discord.Embed(
                title="📘 Menu BoostCoins",
                description="Choisis une section dans le menu déroulant ci-dessous pour voir tes infos.",
                color=discord.Color.blurple()
            )
        else:
            await interaction.response.send_message("❌ Tu n'as pas accès à ce menu.", ephemeral=True)
            return

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(BoostCommands(bot))
