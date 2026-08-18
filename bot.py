import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Anthropic()
user_conversations = {}

SYSTEM_PROMPT = "You are a helpful P6 tutor using My Pals Are Here 3rd Edition textbook. Answer in the SAME language the student uses (Indonesian or English). Topics: Math, Science, English, Bahasa Indonesia. Be fun, simple, and encouraging. When asked for questions, provide the exact number requested and mix MULTIPLE CHOICE (A/B/C/D) with SHORT ANSWER questions. Label difficulty levels if asked. Students can ask anything and you should answer flexibly in their preferred format and language."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    msg = "Hi! I'm your P6 Tutor Bot. Ask me anything about Math, Science, English, or Bahasa Indonesia. You can ask for explanations, questions, or just chat. Type /reset to start fresh."
    await update.message.reply_text(msg)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    await update.message.reply_text("✅ Reset! Start fresh.")

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
            await update.message.reply_text(msg)
    except Exception as e:
