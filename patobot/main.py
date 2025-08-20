import threading
import os
from flask import Flask
from dotenv import load_dotenv

from patobot.config.bot_config import bot

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot.run(TOKEN)
