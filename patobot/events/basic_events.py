import discord
from patobot.config.bot_config import bot


@bot.event
async def on_ready():
    print(f"[OK] Bot conectado como {bot.user}")
    print(f"[INFO] Bot está en {len(bot.guilds)} servidores")
    #Configuracion del estado del bot
    activity = discord.Activity(type=discord.ActivityType.listening, name="!play para música")
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    """Maneja errores de comandos"""
    if isinstance(error, discord.ext.commands.CommandNotFound):
        await ctx.send("❌ Comando no encontrado. Usa `!help` para ver los comandos disponibles.")
    elif isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send("❌ Faltan argumentos requeridos para este comando.")
    elif isinstance(error, discord.ext.commands.BotMissingPermissions):
        await ctx.send("❌ No tengo los permisos necesarios para ejecutar este comando.")
    else:
        print(f"Error en comando {ctx.command}: {error}")
        await ctx.send("❌ Ocurrió un error inesperado.")

@bot.event
async def on_disconnect():
    print("[WARNING] Bot desconectado de Discord")

@bot.event
async def on_resumed():
    print("[INFO] Bot reconectado a Discord")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def pong(ctx):
    await ctx.send("Solo puedes hacer ping crack ")


@bot.command(name="help_music", aliases=["hm"])
async def help_music(ctx):
    """Muestra la ayuda de comandos de música"""
    embed = discord.Embed(
        title="🎵 Comandos de Música",
        description="Lista de comandos disponibles para el bot de música",
        color=0x00ff00
    )

    commands = {
        "!join": "Conecta el bot al canal de voz",
        "!play <canción>": "Reproduce música (URL de YouTube o búsqueda)",
        "!pause": "Pausa la reproducción actual",
        "!resume": "Reanuda la reproducción pausada",
        "!skip": "Salta a la siguiente canción",
        "!stop": "Detiene la música y limpia la cola",
        "!queue": "Muestra la cola de reproducción",
        "!clear": "Limpia la cola de reproducción",
        "!nowplaying": "Muestra la canción actual",
        "!leave": "Desconecta el bot del canal"
    }

    for command, description in commands.items():
        embed.add_field(name=command, value=description, inline=False)

    embed.set_footer(text="También puedes usar alias: !p para !play, !s para !skip, etc.")
    await ctx.send(embed=embed)