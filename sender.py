from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from functions import *


def main():
    """Start the bot."""
    updater = Updater("478708331:AAHjuX1suuValYW3ecbLus97WbGG4Xla3Z8")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('add', start_add_reminder,
                                     pass_chat_data=True)],
        states={
            PERIOD_STATE: [MessageHandler(Filters.text, get_reminder_period,
                                          pass_chat_data=True)],
            MESSAGE_STATE: [MessageHandler(
                Filters.text,
                get_reminder_message_and_finalize_add_reminder,
                pass_job_queue=True,
                pass_chat_data=True
            )]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conversation_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
