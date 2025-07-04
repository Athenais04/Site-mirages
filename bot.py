import sys
import os
import threading
import discord
from discord.ext import commands
from flask import Flask
sys.path.append(os.path.abspath('.'))

# Création de l'app Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Discord BoostCoins en ligne !"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    GUILD_ID = 1382310288115761215  # Remplace par l'ID de ton serveur Discord (type int)

async def setup_hook(self):
    await self.load_extension("cogs.boost")
    print("Cog boost chargé.")
    guild = discord.Object(id=GUILD_ID)
    synced = await self.tree.sync(guild=guild)
    print(f"Slash commands synchronisées sur le serveur {GUILD_ID} : {len(synced)} commandes.")

    async def on_ready(self):
        print(f"Connecté en tant que {self.user} (ID: {self.user.id})")

bot = MyBot()

# Démarrer Flask dans un thread séparé
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

print("Current working directory:", os.getcwd())
print("Content of current dir:", os.listdir('.'))
print("Content of cogs dir:", os.listdir('./cogs') if os.path.exists('./cogs') else "cogs folder not found")

TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)
