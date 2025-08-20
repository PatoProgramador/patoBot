import discord
import yt_dlp
import asyncio
from discord.ext import tasks

from patobot.config.bot_config import bot
from patobot.settings.music_settings import FFMPEG_OPTIONS, YDL_OPTIONS

music_queues = {}

@tasks.loop(seconds=30)
async def keep_alive():
    """Mantiene el bot activo enviando un heartbeat"""
    try:
        for guild in bot.guilds:
            voice_client = guild.voice_client
            if voice_client and voice_client.is_connected():
                channel = voice_client.channel

                # Verificar si hay usuarios humanos en el canal
                human_members = [m for m in channel.members if not m.bot]

                if len(human_members) == 0:
                    # Si no hay humanos, desconectar después de 5 minutos de inactividad
                    if not hasattr(voice_client, 'empty_since'):
                        voice_client.empty_since = asyncio.get_event_loop().time()
                    elif asyncio.get_event_loop().time() - voice_client.empty_since > 300:  # 5 minutos
                        await voice_client.disconnect()
                        music_queues.pop(guild.id, None)
                        print(f"[INFO] Desconectado de {guild.name} por inactividad")
                else:
                    # Reset del timer si hay usuarios
                    if hasattr(voice_client, 'empty_since'):
                        delattr(voice_client, 'empty_since')

                # Mantener conexión activa enviando un "ping" silencioso
                if not voice_client.is_playing() and not voice_client.is_paused():
                    # Reproducir silencio para mantener la conexión
                    if guild.id not in music_queues or not music_queues[guild.id]:
                        try:
                            # Crear un audio silencioso muy corto
                            silence_source = discord.PCMVolumeTransformer(
                                discord.FFmpegPCMAudio("silence.mp3", **{
                                    "before_options": "-f lavfi -t 0.1",
                                    "options": "-vn"
                                }), volume=0.01
                            )
                            # No reproducir realmente, solo mantener la conexión
                        except:
                            pass
    except Exception as e:
        print(f"[ERROR] Error en keep_alive: {e}")

@tasks.loop(seconds=300)  # Cada 5 minutos
async def connection_watchdog():
    """Vigila las conexiones y las restablece si es necesario"""
    try:
        for guild in bot.guilds:
            voice_client = guild.voice_client
            if voice_client:
                # Verificar si la conexión sigue activa
                if not voice_client.is_connected():
                    print(f"[WARNING] Conexión perdida en {guild.name}")
                    # Intentar reconectar si hay usuarios esperando
                    for channel in guild.voice_channels:
                        human_members = [m for m in channel.members if not m.bot]
                        if len(human_members) > 0:
                            try:
                                await channel.connect(timeout=60.0, reconnect=True)
                                print(f"[INFO] Reconectado automáticamente a {channel.name}")
                                break
                            except:
                                print(f"[ERROR] No se pudo reconectar a {channel.name}")
    except Exception as e:
        print(f"[ERROR] Error en connection_watchdog: {e}")

@bot.event
async def on_voice_state_update(member, before, after):
    """Maneja cambios en el estado de voz para evitar desconexiones innecesarias"""
    if member == bot.user:
        return

    # Si el bot está en un canal y se queda solo, desconectarse después de un tiempo
    voice_client = member.guild.voice_client
    if voice_client and voice_client.is_connected():
        channel = voice_client.channel
        # Contar usuarios humanos (no bots)
        human_members = [m for m in channel.members if not m.bot]

        if len(human_members) == 0:
            # Esperar 60 segundos antes de desconectar
            await asyncio.sleep(60)
            # Verificar nuevamente si sigue vacío
            if voice_client.is_connected():
                channel = voice_client.channel
                human_members = [m for m in channel.members if not m.bot]
                if len(human_members) == 0:
                    await voice_client.disconnect()
                    music_queues.pop(member.guild.id, None)

@bot.command()
async def join(ctx):
        # Conecta el bot al canal de voz del usuario
        try:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                if ctx.voice_client:
                    if ctx.voice_client.channel != channel:
                        await ctx.voice_client.move_to(channel)
                        await ctx.send(f"🔄 Movido al canal: **{channel}**")
                    else:
                        await ctx.send("✅ Ya estoy en tu canal de voz.")
                else:
                    await channel.connect(timeout=60.0, reconnect=True)
                    await ctx.send(f"✅ Conectado al canal: **{channel}**")

                    # Iniciar el task de keep_alive si no está corriendo
                    if not keep_alive.is_running():
                        keep_alive.start()
            else:
                await ctx.send("❌ No estás en un canal de voz.")
        except discord.errors.ClientException as e:
            await ctx.send(f"❌ Error de conexión: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ Error inesperado: {str(e)}")

def format_duration(seconds):
    if seconds is None:
        return "Duración desconocida"
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{sec:02d}"
    return f"{minutes}:{sec:02d}"

def play_next(ctx):
    try:
        guild_id = ctx.guild.id
        if guild_id in music_queues and music_queues[guild_id]:
            next_song = music_queues[guild_id].pop(0)

            if ctx.voice_client and ctx.voice_client.is_connected():
                source = discord.FFmpegPCMAudio(next_song["url"], **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda e: play_next_with_error_handling(ctx, e))

                # Enviar mensaje de reproducción
                coro = ctx.send(
                    f"🎵 Reproduciendo: **[{next_song['title']}]({next_song['webpage_url']})** ⏱ {next_song['duration']}")
                asyncio.run_coroutine_threadsafe(coro, bot.loop)
    except Exception as e:
        print(f"Error en play_next: {e}")
        # Intentar reproducir la siguiente canción si hay un error
        if guild_id in music_queues and music_queues[guild_id]:
            play_next(ctx)

def play_next_with_error_handling(ctx, error):
    """Wrapper para manejar errores en play_next"""
    if error:
        print(f"Error de reproducción: {error}")
    play_next(ctx)

@bot.command(name="play", aliasses=["p"])
async def play(ctx, *, search: str):
    """Reproduce música desde YouTube"""
    # Verificar conexión de voz
    if not ctx.voice_client:
        if ctx.author.voice:
            try:
                await ctx.author.voice.channel.connect(timeout=60.0, reconnect=True)
                # Iniciar keep_alive si no está corriendo
                if not keep_alive.is_running():
                    keep_alive.start()
            except Exception as e:
                await ctx.send(f"❌ No pude conectarme al canal: {str(e)}")
                return
        else:
            await ctx.send("❌ Debes estar en un canal de voz para reproducir música.")
            return

    # Mensaje de búsqueda
    search_msg = await ctx.send(f"🔍 Buscando: **{search}**...")

    try:
        ydl_opts_improved = {
            **YDL_OPTIONS,
            "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best[height<=720]",
            "postprocessors": [],  # Sin post-procesamiento
        }
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # Determinar si es URL o búsqueda
            if search.startswith(('http://', 'https://')):
                info = ydl.extract_info(search, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{search}", download=False)

            if "entries" in info and info["entries"]:
                info = info["entries"][0]
            elif not info:
                await search_msg.edit(content="❌ No se encontraron resultados.")
                return

            url = None
            formats = info.get('formats', [])

            # Priorizar formatos de audio específicos
            for fmt in formats:
                if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                    if fmt.get('ext') in ['m4a', 'webm', 'mp3']:
                        url = fmt.get('url')
                        break

            if not url:
                url = info.get('url')

            title = info.get('title', 'Título desconocido')
            webpage_url = info.get('webpage_url', '')
            duration = format_duration(info.get('duration'))

            if not url:
                await search_msg.edit(content="❌ No se pudo obtener la URL del audio.")
                return

        guild_id = ctx.guild.id
        if guild_id not in music_queues:
            music_queues[guild_id] = []

        song_data = {
            "url": url,
            "title": title,
            "webpage_url": webpage_url,
            "duration": duration
        }

        if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
            music_queues[guild_id].append(song_data)
            await search_msg.edit(content=f"📀 Añadido a la cola: **[{title}]({webpage_url})** ⏱ {duration}")
        else:
            try:
                source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)
                ctx.voice_client.play(source, after=lambda e: play_next_with_error_handling(ctx, e))
                await search_msg.edit(content=f"🎵 Reproduciendo: **[{title}]({webpage_url})** ⏱ {duration}")
            except Exception as e:
                await search_msg.edit(content=f"❌ Error al reproducir: {str(e)}")

    except Exception as e:
        await search_msg.edit(content=f"❌ Error durante la búsqueda: {str(e)}")
        print(f"Error en comando play: {e}")

@bot.command(name="skip", aliases=["s"])
async def skip(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send("⏭ Saltando a la siguiente canción...")
    else:
        await ctx.send("❌ No hay nada reproduciéndose.")

@bot.command(name="pause")
async def pause(ctx):
    """Pausa la reproducción"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸ Música pausada.")
    else:
        await ctx.send("❌ No hay nada reproduciéndose.")

@bot.command(name="resume")
async def resume(ctx):
    """Reanuda la reproducción"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶ Música reanudada.")
    else:
        await ctx.send("❌ La música no está pausada.")

@bot.command(name="stop")
async def stop(ctx):
    """Detiene la reproducción y limpia la cola"""
    if ctx.voice_client:
        ctx.voice_client.stop()
        music_queues[ctx.guild.id] = []
        await ctx.send("⏹ Reproducción detenida y cola limpiada.")
    else:
        await ctx.send("❌ No hay nada reproduciéndose.")

@bot.command(name="queue", aliasses=["q"])
async def show_queue(ctx):
    """Muestra la cola de reproducción"""
    guild_id = ctx.guild.id
    if guild_id not in music_queues or not music_queues[guild_id]:
        await ctx.send("📭 La cola está vacía.")
        return

    queue_list = "\n".join([
        f"{i + 1}. **{song['title'][:50]}{'...' if len(song['title']) > 50 else ''}** ⏱ {song['duration']}"
        for i, song in enumerate(music_queues[guild_id][:10])  # Mostrar solo las primeras 10
    ])

    total_songs = len(music_queues[guild_id])
    if total_songs > 10:
        queue_list += f"\n... y {total_songs - 10} canciones más"

    embed = discord.Embed(title="📜 Cola de Reproducción", description=queue_list, color=0x00ff00)
    await ctx.send(embed=embed)

@bot.command(name="clear")
async def clear_queue(ctx):
    """Limpia la cola de reproducción"""
    guild_id = ctx.guild.id
    if guild_id in music_queues:
        cleared_count = len(music_queues[guild_id])
        music_queues[guild_id] = []
        await ctx.send(f"🗑 Cola limpiada. Se eliminaron {cleared_count} canciones.")
    else:
        await ctx.send("📭 La cola ya está vacía.")

@bot.command()
async def leave(ctx):
    """Desconecta el bot del canal de voz"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect(force=True)
        music_queues.pop(ctx.guild.id, None)
        await ctx.send("👋 Desconectado del canal de voz.")
    else:
        await ctx.send("❌ No estoy en un canal de voz.")

@bot.command(name="nowplaying", aliases=["np"])
async def now_playing(ctx):
    """Muestra información de la canción actual"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        await ctx.send("🎵 Hay música reproduciéndose actualmente.")
    elif ctx.voice_client and ctx.voice_client.is_paused():
        await ctx.send("⏸ La música está pausada.")
    else:
        await ctx.send("❌ No hay nada reproduciéndose.")