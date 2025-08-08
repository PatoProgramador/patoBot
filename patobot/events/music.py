import discord
import yt_dlp

from patobot.config.bot_config import bot

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("❌ No estás en un canal de voz.")

@bot.command()
async def play(ctx, *, url):
    if not ctx.author.voice:
        await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")
        return

    voice_channel = ctx.author.voice.channel
    vc = ctx.voice_client

    if not vc:
        vc = await voice_channel.connect()

    if vc.is_playing():
        vc.stop()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info["url"]

    vc.play(discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS))
    await ctx.send(f"🎶 Reproduciendo: **{info['title']}**")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("❌ No estoy en un canal de voz.")
