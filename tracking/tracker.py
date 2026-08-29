import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from telegram import LinkPreviewOptions

import scraping
from .registration import load_users, save_user
from paths import base_dir


load_dotenv(base_dir() / ".env")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

logger = logging.getLogger(__name__)


class Tracker:
    def __init__(self, token: str = TELEGRAM_BOT_TOKEN) -> None:
        if not token:
            raise RuntimeError(
                "TELEGRAM_BOT_TOKEN is not set. Create a .env file next to the "
                "executable (see .env.example) with your own bot token."
            )
        self._application = Application.builder().token(token).post_init(self.post_init).build()
        self._application.add_handler(CommandHandler("start", self.start))
        self._application.job_queue.run_repeating(self.check_updates, interval=360)

    async def post_init(self, application: Application) -> None:
        await self.check_updates(None)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        save_user(update.effective_chat.id)
        await update.message.reply_text("Your chat has been registered.")

    async def broadcast(self, text: str) -> None:
        users = load_users()
        logger.info("Sending update to %d users.", len(users))
        for chat_id in users:
            try:
                await self._application.bot.send_message(chat_id=chat_id, text=text,
                parse_mode=ParseMode.MARKDOWN, link_preview_options=LinkPreviewOptions(is_disabled=True),)
            except Exception:
                logger.exception("Could not send message to %s.", chat_id)

    async def check_updates(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        logger.info("Running scrapers...")
        for scraper in scraping.ScrapersList:
            try:
                if message := scraper.run():
                    await self.broadcast(message)
            except Exception:
                logger.exception("Scraper %s failed.", scraper.name)

    def run(self) -> None:
        logger.info("Starting tracker...")
        self._application.run_polling()
