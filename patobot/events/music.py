import discord
import yt_dlp

from patobot.config.bot_config import bot
from patobot.settings.music_settings import FFMPEG_OPTIONS, YDL_OPTIONS

music_queues = {}

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("❌ No estás en un canal de voz.")

def format_duration(seconds):
    minutes, sec = divmod(seconds, 60)
    return f"{minutes}:{sec:02d}"

def play_next(ctx):
    guild_id = ctx.guild.id
    if music_queues.get(guild_id):
        next_song = music_queues[guild_id].pop(0)
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(next_song["url"], **FFMPEG_OPTIONS),
            after=lambda e: play_next(ctx)
        )
        coro = ctx.send(f"🎵 Reproduciendo: **[{next_song['title']}]({next_song['webpage_url']})** ⏱ {next_song['duration']}")
        bot.loop.create_task(coro)

@bot.command(name="play")
async def play(ctx, *, search: str):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ Debes estar en un canal de voz para reproducir música.")
        return

    if ctx.voice_client is None:
        await ctx.author.voice.channel.connect()

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
        webpage_url = info['webpage_url']
        duration = format_duration(info['duration'])

    guild_id = ctx.guild.id
    if guild_id not in music_queues:
        music_queues[guild_id] = []

    song_data = {
        "url": url,
        "title": title,
        "webpage_url": webpage_url,
        "duration": duration
    }

    if ctx.voice_client.is_playing():
        music_queues[guild_id].append(song_data)
        await ctx.send(f"📀 Añadido a la cola: **[{title}]({webpage_url})** ⏱ {duration}")
    else:
        ctx.voice_client.play(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=lambda e: play_next(ctx)
        )
        await ctx.send(f"🎵 Reproduciendo: **[{title}]({webpage_url})** ⏱ {duration}")

@bot.command(name="skip")
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ Saltando a la siguiente canción...")
    else:
        await ctx.send("❌ No hay nada reproduciéndose.")

@bot.command(name="queue")
async def show_queue(ctx):
    guild_id = ctx.guild.id
    if guild_id not in music_queues or not music_queues[guild_id]:
        await ctx.send("📭 La cola está vacía.")
        return

    queue_list = "\n".join([
        f"{i+1}. {song['title']} ⏱ {song['duration']}"
        for i, song in enumerate(music_queues[guild_id])
    ])
    await ctx.send(f"📜 **Cola de reproducción:**\n{queue_list}")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("❌ No estoy en un canal de voz.")
