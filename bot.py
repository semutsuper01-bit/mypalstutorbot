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
1. Always answer in ENGLISH, even if the student asks in Indonesian
2. Explain topics in a detailed and fun way that's easy to remember
3. If asked for questions, provide 3 sets: Easy, Medium, Hard
4. Focus only on topics from "My Pals Are Here 3rd Edition"
5. Keep responses engaging and age-appropriate for P6 students

When a student asks:
- "Explain [topic]" → Give detailed, fun explanation with examples
- "Give me questions" → Provide Easy/Medium/Hard questions
- "Answer [topic]" → Answer their specific question
- "/reset" → Clear conversation history for that user"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    
    msg = """Hello! I'm your My Pals Tutor Bot! 👋

I can help you with:
📚 Mathematics (P6)
🔬 Science (P6)
🇬🇧 English (P6)
🇮🇩 Bahasa Indonesia (P6)

Examples:
- "Explain fractions"
- "Give me questions about photosynthesis"
- "What is a noun?"
- "Jelaskan bilangan bulat"

Type /reset to start a new topic."""
    
    await update.message.reply_text(msg)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    await update.message.reply_text("✅ Conversation reset! Start with a new topic.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    user_conversations[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    await update.message.chat.send_action("typing")
    
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=user_conversations[user_id]
        )
        
        assistant_message = response.content[0].text
        
        user_conversations[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        if len(assistant_message) > 4096:
            for chunk in [assistant_message[i:i+4096] for i in range(0, len(assistant_message), 4096)]:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(assistant_message)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

def main():
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("Missing TELEGRAM_BOT_TOKEN")
        return
    
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
