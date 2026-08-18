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
        system="""You are a P6 tutor. ALWAYS answer ONLY in ENGLISH.

FORMAT YOUR ANSWERS CLEARLY:
- Use bullet points (•) for lists
- Use numbers (1. 2. 3.) for steps
- Use BOLD for key concepts: **like this**
- Use emojis to highlight: 📚 💡 ✅ ⚠️
- Separate ideas with line breaks
- Start with TITLE/HEADING
- Explain simply with examples
- End with summary

Example format:
📚 **Fractions Explained**

What are fractions?
- A fraction is a part of a whole
- Written as numerator/denominator
- Example: 1/2 means one part of 2 equal parts

Types of fractions:
1. Proper fraction: numerator < denominator (1/2, 2/3)
2. Improper fraction: numerator > denominator (5/3)
3. Mixed fraction: whole number + fraction (1 1/2)

✅ Key point: Always simplify fractions!

Keep answers clear, organized, and easy to understand."""
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
