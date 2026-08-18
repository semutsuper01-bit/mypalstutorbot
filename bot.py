import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

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

LANGUAGE RULE: No matter if student writes \"Jelaskan fotosintesis\" or \"Explain photosynthesis\", you ALWAYS reply in ENGLISH ONLY.\"\"\"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command and welcome the user."""
    user = update.effective_user
    user_id = update.effective_chat.id
    conversations[user_id] = []

    welcome_message = (
        f"👋 Hi {user.first_name}!\n\n"
        "I'm your P6 tutor, here to help you with Math, Science, English, and "
        "Bahasa Indonesia based on the *My Pals Are Here 3rd Edition* curriculum.\n\n"
        "🎯 Ask me to explain a topic, or ask for practice questions "
        "(easy, medium, or hard).\n\n"
        "Let's make learning fun! What would you like to learn today?"
    )
    await update.message.reply_text(welcome_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming text messages by forwarding them to Claude."""
    user_id = update.effective_chat.id
    user_message = update.message.text

    if user_id not in conversations:
        conversations[user_id] = []

    conversations[user_id].append({"role": "user", "content": user_message})

    await context.bot.send_chat_action(chat_id=user_id, action="typing")

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=conversations[user_id],
        )

        reply_text = "".join(
            block.text for block in response.content if hasattr(block, "text")
        )

        conversations[user_id].append({"role": "assistant", "content": reply_text})

        await update.message.reply_text(reply_text)
    except Exception:
        logger.exception("Error while getting response from Claude")
        conversations[user_id].pop()
        await update.message.reply_text(
            "😅 Sorry, I ran into an error while thinking about that. Please try again."
        )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error("Update %s caused error %s", update, context.error)

    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "😅 Something went wrong. Please try again in a moment."
            )
        except Exception:
            logger.exception("Failed to notify user about the error")


def main() -> None:
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")
    if not anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable is not set")

    application = Application.builder().token(telegram_bot_token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)

    logger.info("Starting bot polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
