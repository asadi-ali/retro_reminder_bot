from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from functions import *
from settings import ACCESS_TOKEN


def main():
    """Start the bot."""
    updater = Updater(ACCESS_TOKEN)
    dp = updater.dispatcher

    add_command_handler = ConversationHandler(
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

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("delete", delete, pass_chat_data=True))
    dp.add_handler(add_command_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
