import discord
from discord.ext import commands, tasks
from discord import app_commands
from database import add_coins, remove_coins, get_balance
import sqlite3

# -------------------- CONFIG --------------------
GUILD_ID = 1382310288115761215
CHANNEL_ID = 1382315923427295275
DB_PATH = "boostcoins.db"  # Assure-toi que c’est bien le nom correct

# -------------------- DATABASE FUNCTIONS --------------------
def get_balance(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0

def add_coins(user_id: int, amount: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, coins) VALUES (?, 0)", (user_id,))
    cur.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def remove_coins(user_id: int, amount: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (user_id, coins) VALUES (?, 0)", (user_id,))
    cur.execute("UPDATE users SET coins = MAX(coins - ?, 0) WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_top_users(limit=3):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, coins FROM users ORDER BY coins DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_inventory(user_id):
    return ["🎁 Pack Bonus", "💎 Gemme rare"]

def get_shop_items():
    return [
        ("🔥 Boost XP", "Double ton XP pendant 1h", 300),
        ("📦 Pack Mystère", "Contient un objet aléatoire", 500),
        ("🎫 Ticket VIP", "Accès VIP pendant 24h", 1000)
    ]

# -------------------- UI SELECT MENU --------------------
class BoostHelpSelect(discord.ui.Select):
    def __init__(self, parent_view):
        options = [
            discord.SelectOption(label="Solde & Classement", value="balance", emoji="💰"),
            discord.SelectOption(label="Boutique", value="shop", emoji="🛍️"),
            discord.SelectOption(label="Casino", value="casino", emoji="🎰"),
            discord.SelectOption(label="Commandes Admin", value="admin", emoji="🛠️"),
        ]
        super().__init__(
            placeholder="📂 Choisis une catégorie...",
            options=options,
            custom_id="boostcoins_menu"
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        await self.parent_view.update_embed(interaction, self.values[0])

# -------------------- UI VIEW --------------------
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
            embed.add_field(
                name="🛒 Objets disponibles",
                value="\n".join([f"{name} — {price} 💰\n> {desc}" for name, desc, price in items]),
                inline=True
            )

        elif choice == "casino":
            embed.title = "🎰 Casino"
            embed.description = (
                "`/roulette` — Parie sur un numéro ou une couleur\n"
                "`/dice` — Lance les dés contre le bot\n"
                "`/blackjack` — Joue contre la banque"
            )

        elif choice == "admin":
            embed.title = "🛠️ Commandes Admin"
            embed.description = (
                "`/addcoins @membre montant` — Ajouter des BoostCoins\n"
                "`/removecoins @membre montant` — Retirer des BoostCoins\n"
                "`/edititem` — Modifier un item de la boutique\n"
                "`/postboost` — Afficher le menu manuellement"
            )

        await interaction.response.edit_message(embed=embed, view=self)

# -------------------- COG --------------------
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
                description="Choisis une catégorie dans le menu déroulant ci-dessous pour voir les infos.",
                color=discord.Color.blurple()
            )
            view = BoostHelpView(user=self.bot.user)
            await channel.send(embed=embed, view=view)

    @app_commands.command(name="addcoins", description="Ajouter des BoostCoins à un membre.")
    @app_commands.checks.has_permissions(administrator=True)
    async def addcoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ Le montant doit être positif.", ephemeral=True)
            return
        add_coins(member.id, amount)
        await interaction.response.send_message(f"✅ {amount} BoostCoins ajoutés à {member.display_name}.", ephemeral=True)

    @app_commands.command(name="removecoins", description="Retirer des BoostCoins à un membre.")
    @app_commands.checks.has_permissions(administrator=True)
    async def removecoins(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if amount <= 0:
            await interaction.response.send_message("❌ Le montant doit être positif.", ephemeral=True)
            return
        current = get_balance(member.id)
        if current < amount:
            await interaction.response.send_message(f"❌ {member.display_name} n’a que {current} BoostCoins.", ephemeral=True)
            return
        remove_coins(member.id, amount)
        await interaction.response.send_message(f"✅ {amount} BoostCoins retirés à {member.display_name}.", ephemeral=True)

    @app_commands.command(name="postboost", description="Affiche manuellement le menu BoostCoins dans ce salon.")
    @app_commands.checks.has_permissions(administrator=True)
    async def postboost(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 Menu BoostCoins",
            description="Choisis une catégorie dans le menu déroulant ci-dessous pour voir les infos.",
            color=discord.Color.blurple()
        )
        view = BoostHelpView(user=interaction.user)
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Menu BoostCoins affiché ici.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(BoostCommands(bot))
