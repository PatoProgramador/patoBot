import discord
import os
from discord.ext import commands

if not discord.opus.is_loaded():
    possible_paths = [
        "/opt/homebrew/lib/libopus.dylib",
        "/usr/local/lib/libopus.dylib",
        "libopus.so",
        "opus.dll"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            discord.opus.load_opus(path)
            print(f"✅ Opus cargado desde {path}")
            break
    else:
        print("❌ No se encontró libopus. Instálalo con 'brew install opus' o 'apt install libopus-dev'.")



intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
