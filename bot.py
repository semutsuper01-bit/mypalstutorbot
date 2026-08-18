import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

client = Anthropic()
conversations = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations[user_id] = []
    await update.message.reply_text("Hi! Ask me anything!")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conversations[update.effective_user.id] = []
    await update.message.reply_text("Reset!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in conversations:
        conversations[user_id] = []
    
    conversations[user_id].append({"role": "user", "content": text})
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        system="You are a P6 tutor. ALWAYS answer in ENGLISH, even if student asks in Indonesian or other languages. Never respond in any language except English.",
        messages=conversations[user_id]
    )
    
    answer = response.content[0].text
    conversations[user_id].append({"role": "assistant", "content": answer})
    await update.message.reply_text(answer)

app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
