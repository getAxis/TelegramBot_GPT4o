#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import openai
import os
from openai import OpenAI

# Вставь сюда свой API ключ от OpenAI
OPENAI_API_KEY = "OPENAI_API_KEY"
openai.api_key = OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

# Вставь сюда токен бота от Telegram
TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Переменная для хранения истории диалога
conversation_history = {}

async def start(update: Update, context: CallbackContext) -> None:
    """Отправляет приветственное сообщение при команде /start."""
    user = update.effective_user
    await update.message.reply_markdown_v2(
        fr'Привет, {user.mention_markdown_v2()}\! Я бот на основе GPT\-4\. Задай мне вопрос\!',
        reply_markup=ForceReply(selective=True),
    )

async def new_conversation(update: Update, context: CallbackContext) -> None:
    """Очищает историю диалога при команде /new."""
    user_id = update.effective_user.id
    conversation_history[user_id] = []
    await update.message.reply_text('История диалога очищена!')

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Отвечает на сообщение пользователя."""
    user_id = update.effective_user.id
    user_message = update.message.text

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append(user_message)

    # Создаем запрос к модели GPT-4
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens = 1024,
        messages=[
            
            {"role": "system", "content": "You are a helpful assistant."}
        ] + [{"role": "user", "content": msg} for msg in conversation_history[user_id]]
    )

    bot_response = response.choices[0].message.content
    conversation_history[user_id].append(bot_response)

    await update.message.reply_text(bot_response)

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("new", new_conversation))

    # Обработчик сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()