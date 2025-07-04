class BoostHelpSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Solde & Classement", value="balance", emoji="💰"),
            discord.SelectOption(label="Boutique", value="shop", emoji="🛍️"),
            discord.SelectOption(label="Jeux de casino", value="casino", emoji="🎰"),
            discord.SelectOption(label="Commandes Admin", value="admin", emoji="🛠️"),
        ]
        super().__init__(placeholder="📂 Choisis une catégorie...", options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = self.values[0]
        await self.view.update_embed(interaction, choice)  # APPELLE update_embed DE LA VIEW


class BoostHelpView(discord.ui.View):
    def __init__(self, user: discord.User):
        super().__init__(timeout=None)
        self.user = user
        self.select = BoostHelpSelect()
        self.add_item(self.select)
        self.message = None

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
        # Tu peux commenter la ligne suivante si tu veux utiliser uniquement la commande postboost
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
            msg = await channel.send(embed=embed, view=view)
            view.message = msg

    @app_commands.command(name="postboost", description="Affiche manuellement le menu BoostCoins dans ce salon.")
    @app_commands.checks.has_permissions(administrator=True)
    async def postboost(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 Aide BoostCoins",
            description="Choisis une catégorie dans le menu déroulant ci-dessous pour voir les commandes et infos en direct.",
            color=discord.Color.blurple()
        )
        view = BoostHelpView(user=interaction.user)
        msg = await interaction.channel.send(embed=embed, view=view)
        view.message = msg
        await interaction.response.send_message("✅ Menu BoostCoins publié dans ce salon.", ephemeral=True)
