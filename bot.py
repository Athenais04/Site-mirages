import os
import threading
import discord
from discord.ext import commands
from flask import Flask

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

    async def setup_hook(self):
        # Charger ta cog boost
        await self.load_extension("cogs.boost")
        print("Cog boost chargé.")
        # Synchroniser les slash commands globales
        synced = await self.tree.sync()
        print(f"Slash commands synchronisées : {len(synced)} commandes.")

    async def on_ready(self):
        print(f"Connecté en tant que {self.user} (ID: {self.user.id})")

bot = MyBot()

# Démarrer Flask dans un thread séparé
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)
