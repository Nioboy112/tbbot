from telegram import Update
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackContext
import subprocess

# States for the conversation handler
INPUT_LINK, INPUT_PASSWORD = range(2)

# /start command handler
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Welcome! Use /generate to run the script.')
    return ConversationHandler.END

# /generate command handler
def generate(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Please provide the Terabox link:')
    return INPUT_LINK

# Collect Terabox link
def collect_link(update: Update, context: CallbackContext) -> int:
    context.user_data['link'] = update.message.text
    update.message.reply_text('Please provide the password (if any), or type /skip:')
    return INPUT_PASSWORD

# Collect password
def collect_password(update: Update, context: CallbackContext) -> int:
    user_input = update.message.text
    if user_input == '/skip':
        context.user_data['password'] = ''
    else:
        context.user_data['password'] = user_input
    run_script(update)
    return ConversationHandler.END

# Execute the run.py script
def run_script(update: Update) -> None:
    link = context.user_data['link']
    password = context.user_data['password']

    # Run the script with provided inputs
    result = subprocess.run(['python3', 'run.py', link, password], capture_output=True, text=True)

    # Send the output of the script execution to the user
    update.message.reply_text(result.stdout)
    if result.stderr:
        update.message.reply_text(f"Error: {result.stderr}")

def main() -> None:
    # Initialize the Telegram Bot
    updater = Updater("YOUR_BOT_TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("generate", generate)],
        states={
            INPUT_LINK: [MessageHandler(Filters.text & ~Filters.command, collect_link)],
            INPUT_PASSWORD: [MessageHandler(Filters.text & ~Filters.command, collect_password)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
