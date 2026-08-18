import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Anthropic()
user_conversations = {}

SYSTEM_PROMPT = "You are a helpful P6 tutor. Answer in the same language student uses. Topics: Math, Science, English, Bahasa Indonesia. Be fun and simple. When asked for questions, provide exact number and mix ABCD choices with short answer. Label difficulty if asked."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    msg = "Hi! I'm your P6 Tutor. Ask me anything about Math, Science, English, or Bahasa Indonesia. Type /reset to start fresh."
    await update.message.reply_text(msg)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    await update.message.reply_text("Reset!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    user_conversations[user_id].append({"role": "user", "content": user_message})
    await update.message.chat.send_action("typing")
    
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=user_conversations[user_id]
        )
        
        msg = response.content[0].text
        user_conversations[user_id].append({"role": "assistant", "content": msg})
        
        if len(msg) > 4096:
            for chunk in [msg[i:i+4096] for i in range(0, len(msg), 4096)]:
                await update.message.reply_text(chunk)
        else:
            await
