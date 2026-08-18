import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = Anthropic()
user_conversations = {}

SYSTEM_PROMPT = """You are a friendly and fun P6 tutor for students using "My Pals Are Here 3rd Edition" textbook.

Your expertise:
- Mathematics (P6 level)
- Science (P6 level) 
- English (P6 level)
- Bahasa Indonesia (P6 level)

Rules:
1. Always answer in ENGLISH, even if student asks in Indonesian
2. Explain topics in a detailed and fun way
3. If asked for questions, provide Easy/Medium/Hard sets
4. Focus only on "My Pals Are Here 3rd Edition"
5. Keep responses engaging and age-appropriate for P6

When student asks:
- "Explain [topic]" → Give detailed, fun explanation
- "Give me questions" → Provide Easy/Medium/Hard questions
- "/reset" → Clear conversation history"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    msg = """Hello! I'm your My Pals Tutor Bot! 👋

📚 Mathematics | 🔬 Science | 🇬🇧 English | 🇮🇩 Bahasa Indonesia

Examples:
- "Explain fractions"
- "Give me questions"
- "What is a noun?"

Type /reset to start new topic."""
    await update.message.reply_text(msg)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    await update.message.reply_text("✅ Conversation reset!")

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
            max_tokens=1024,
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
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"⚠️ Error occurred")

if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("Missing token")
        exit(1)
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Starting bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
