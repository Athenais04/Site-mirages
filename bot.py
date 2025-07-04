import os
import discord
from discord.ext import commands

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

TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)
