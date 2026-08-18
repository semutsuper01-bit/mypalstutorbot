import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

# Inisialisasi Anthropic client
client = Anthropic()

# Conversation history per user (untuk memory)
user_conversations = {}

# System prompt bot
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
6. If asked to reset topic, start fresh

When a student asks:
- "Explain [topic]" → Give detailed, fun explanation with examples
- "Give me questions" → Provide Easy/Medium/Hard questions
- "Answer [topic]" → Answer their specific question
- "/reset" → Clear conversation history for that user"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    
    welcome_message = """Hello! I'm your My Pals Tutor Bot! 👋

I can help you with:
📚 **Mathematics** (P6 level)
🔬 **Science** (P6 level)
🇬🇧 **English** (P6 level)
🇮🇩 **Bahasa Indonesia** (P6 level)

Just type your question or topic, and I'll explain it in a fun way!

Example questions:
- "Explain fractions"
- "Give me questions about photosynthesis"
- "What is a noun?" 
- "Jelaskan tentang bilangan bulat"

Type /reset if you want to start a new topic."""
    
    await update.message.reply_text(welcome_message)

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reset conversation history for user"""
    user_id = update.effective_user.id
    user_conversations[user_id] = []
    await update.message.reply_text("✅ Conversation reset! Start with a new topic.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Initialize conversation if not exists
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    # Add user message to history
    user_conversations[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Show typing indicator
    await update.message.chat.send_action("typing")
    
    try:
        # Call Anthropic API with conversation history
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=user_conversations[user_id]
        )
        
        # Extract response text
        assistant_message = response.content[0].text
        
        # Add to conversation history
        user_conversations[user_id].append({
            "role": "assistant",
            "content": assistant_message
        })
        
        # Send response (split if too long)
        if len(assistant_message) > 4096:
            for chunk in [assistant_message[i:i+4096] for i in range(0, len(assistant_message), 4096)]:
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text(assistant_message)
            
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}\n\nPlease try again.")
        print(f"Error: {e}")

async def main():
    """Start the bot"""
    # Get tokens from environment
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not telegram_token or not anthropic_key:
        print("ERROR: TELEGRAM_BOT_TOKEN or ANTHROPIC_API_KEY not set!")
        return
    
    # Create application
    application = Application.builder().token(telegram_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reset", reset))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    await application.run_polling()

if __name__ == '__main__':
    import asyncio
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            pass
        else:
            raise
