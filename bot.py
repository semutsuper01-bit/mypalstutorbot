import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

client = Anthropic()
user_convos = {}

SYSTEM = "You are P6 tutor. Always answer in English. Help with Math, Science, English, Bahasa Indonesia. Be fun and clear. When asked for questions, provide the number requested with mix of A/B/C/D and short answer questions."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_convos[update.effective_user.id] = []
    await update.message.reply_text("Hi! Ask me anything about P6 topics. /reset to start fresh.")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_convos[update.effective_user.id] = []
    await update.message.reply_text("Reset!")

async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    if uid not in user_convos:
        user_convos[uid] = []
    
    user_convos[uid].append({"role": "user", "content": text})
    await update.message.chat.send_action("typing")
    
    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM,
            messages=user_convos[uid]
        )
        reply = resp.content[0].text
        user_convos[uid].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except:
        await update.message.reply_text("Error")

if __name__ == '__main__':
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, msg))
    app.run_polling()
