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
    # Pour Render, écoute sur le port défini par la variable d'env PORT, sinon 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")
    try:
        await bot.load_extension("cogs.boost")
        print("Cog boost chargé.")
    except Exception as e:
        print(f"Erreur chargement cog: {e}")

# Démarrer Flask dans un thread séparé
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)
