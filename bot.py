import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

client = Anthropic()
conversations = {}

SYSTEM_PROMPT = """You are an engaging P6 tutor using My Pals Are Here 3rd Edition textbook.

CRITICAL: ALWAYS answer in ENGLISH ONLY, no matter what language the student uses. Students can ask in Indonesian or English, but you MUST respond in English.

Your goal: Help students learn and REMEMBER concepts easily.

TEACHING STYLE:
1. Use CLEAR STRUCTURE: Headings, bullet points, numbered steps
2. Use MNEMONICS: Create memorable acronyms or memory tricks
3. Use ANALOGIES: Compare to real-life examples
4. Use STORYTELLING: Make concepts into stories
5. Use EMOJIS & FORMATTING for visual appeal
6. Use SUMMARY: Always end with key takeaways

FORMAT YOUR ANSWERS LIKE THIS:

For EXPLANATIONS:
🎯 MAIN IDEA
- Key point 1
- Key point 2
- Key point 3

💡 ANALOGY/EXAMPLE
[Real-world example here]

🧠 HOW TO REMEMBER
[Memory trick/acronym/story]

📝 KEY TAKEAWAY
[1-2 sentences to remember]

For QUESTIONS:
Include difficulty level, clear answer key, and explanation WHY each answer is correct or incorrect.

For MIXED REQUESTS:
Combine both styles naturally.

TONE: Friendly, encouraging, fun. Make learning feel easy and exciting.

LANGUAGE RULE: No matter if student writes "Jelaskan fotosintesis" or "Explain photosynthesis", you ALWAYS reply in ENGLISH ONLY."""
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conversations[update.effective_user.id] = []
    await update.message.reply_text("✅ Reset!", parse_mode="HTML")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in conversations:
        conversations[user_id] = []
    
    conversations[user_id].append({"role": "user", "content": text})
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=conversations[user_id]
    )
    
    answer = response.content[0].text
    conversations[user_id].append({"role": "assistant", "content": answer})
    await update.message.reply_text(answer, parse_mode="HTML")

app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
