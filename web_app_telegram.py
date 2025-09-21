import os
import functools
import json
from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from fundamental_analysis.stock_rag import StockAnalysisRAG

from dotenv import load_dotenv

rag_instance = StockAnalysisRAG()
# Replace with your actual RAG pipeline function


@functools.lru_cache(maxsize=128)
def rag_pipeline(stock: str, sector: str, entry_price: float, cmp: float) -> str:
    response = rag_instance.query_model(
        stock_name=stock, stock_category=sector, entry_price=entry_price, cmp=cmp)
    # dummy implementation for testing
    # return f"Analysis for {stock} at entry {entry_price}: 🚀 Dummy RAG output"
    return response


# Define a `/start` command handler.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message with a button that opens a the web app."""
    await update.message.reply_text(
        "Please press the button below to get fundamental analysis of a stock using AI Model",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text="📊 Stock Analysis WebApp",
                web_app=WebAppInfo(
                    url="https://aqua-4.github.io/telegram_algo_trader_llm"),
            )
        ),
    )


# Handle data returned from WebApp
async def handle_webapp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.message.web_app_data.data  # JSON from WebApp
    payload = json.loads(data)
    print(payload)
    stock = payload["stock"]
    sector = payload["sector"]
    entry_price = payload["price"]
    cmp = payload["currentPrice"]

    try:
        # Inform user to wait
        await update.message.reply_text("⏳ Please wait while we analyse the stock...")
        sebi_safegaurd = "The stock fundamental analysis presented here is generated only as a proof of concept (POC) for educational purposes. It is not intended as financial advice, investment advice, or a recommendation to buy, sell, or hold any security. Please consult a SEBI-registered financial advisor before making investment decisions."
        await update.message.reply_text(sebi_safegaurd)

        result = rag_pipeline(stock, sector, entry_price=entry_price, cmp=cmp)
        await update.message.reply_text(f"📈 {result}")
    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        await update.message.reply_text(f"❌ Error: Failed to generate data, contact admin.")


def main() -> None:
    """Start the bot."""
    load_dotenv('telegram.env')
    botname = 'aqua4_algotrader_bot'
    BOT_TOKEN = os.environ[botname]
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    # application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, rag_pipeline))
    application.add_handler(MessageHandler(
        filters.StatusUpdate.WEB_APP_DATA, handle_webapp))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
