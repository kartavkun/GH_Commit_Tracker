# src/telegram_bot.py
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from commit_tracker import CommitTracker
import os
from dotenv import load_dotenv

load_dotenv()

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.application = Application.builder().token(self.token).build()

        # Setup logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Add command handler
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Привет! Отправь мне ссылку на репозиторий GitHub, чтобы начать отслеживать коммиты.")

    async def handle_message(self, update: Update, context: CallbackContext):
        repo_url = update.message.text.strip()
        chat_id = update.message.chat_id
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

        # Inform the user
        await update.message.reply_text(f"Начинаю отслеживать репозиторий: {repo_url}")

        # Start the CommitTracker
        commit_tracker = CommitTracker(
            repo_url=repo_url,
            bot_token=bot_token,
            chat_id=chat_id
        )
        commit_tracker.track_commits()

    def start_bot(self):
        self.application.run_polling()
