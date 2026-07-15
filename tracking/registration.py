import json
import os
import asyncio
import logging
from dotenv import load_dotenv

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


load_dotenv()
JSON_FILE = os.getenv("USERS_RECORDS_PATH")

logger = logging.getLogger(__name__)


def load_users() -> list:
    if not os.path.exists(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_user(chat_id: int):
    users = load_users()
    if chat_id not in users:
        users.append(chat_id)
        with open(JSON_FILE, "w") as f:
            json.dump(users, f, indent=4)
        logging.info(f"Saved new user ID: {chat_id}")
