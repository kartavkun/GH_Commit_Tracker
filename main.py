# main.py
import sys
import os
from dotenv import load_dotenv

# Добавляем путь к src в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from telegram_bot import TelegramBot
load_dotenv()

if __name__ == "__main__":
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("Please set TELEGRAM_BOT_TOKEN in your .env file")
    else:
        bot = TelegramBot(token=bot_token)
        bot.start_bot()
