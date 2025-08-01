import sys
import os
import threading
import discord
from discord.ext import commands
from discord import app_commands
from flask import Flask

# Import et initialisation base de données
from database import init_db, add_coins, get_balance

init_db()

# Exemple d'utilisation
user_id_example = 123456
add_coins(user_id_example, 50)
balance = get_balance(user_id_example)
print(f"Solde pour l'user {user_id_example} : {balance} coins")

# Flask app
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot Discord BoostCoins en ligne !"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ID de ton serveur Discord (assure-toi qu'il est correct)
GUILD_ID = 1382310288115761215

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

# Bot personnalisé
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.load_extension("cogs.boost")
        print("✅ Cog boost chargé.")
        guild = discord.Object(id=GUILD_ID)
        synced = await self.tree.sync(guild=guild)
        print(f"✅ Slash commands synchronisées : {len(synced)} sur le serveur {GUILD_ID}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user} (ID: {bot.user.id})")

@bot.tree.command(name="sync", description="Force la sync des commandes")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def sync(interaction: discord.Interaction):
    synced = await bot.tree.sync(guild=interaction.guild)
    await interaction.response.send_message(f"🔄 {len(synced)} commandes synchronisées", ephemeral=True)

# Thread Flask
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Logs utiles
print("Current working directory:", os.getcwd())
print("Content of current dir:", os.listdir('.'))
print("Content of cogs dir:", os.listdir('./cogs') if os.path.exists('./cogs') else "cogs folder not found")

# Lancer le bot
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Le token Discord n'est pas défini dans les variables d'environnement.")
else:
    bot.run(TOKEN)

