from patobot.config.bot_config import bot


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

