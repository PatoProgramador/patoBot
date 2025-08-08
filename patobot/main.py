import threading
import os
from flask import Flask
from dotenv import load_dotenv

from patobot.config.bot_config import bot

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Running PatoBot B)"

def run_flask():
    app.run(host="0.0.0.0", port=8080)


if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)
