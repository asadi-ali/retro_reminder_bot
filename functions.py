import logging
from telegram.ext import ConversationHandler
import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)
PERIOD_STATE, MESSAGE_STATE = range(2)


def _reminder(bot, job):
    bot.send_message(**job.context)


def _get_seconds_from_now_to_night():
    today_night = datetime.datetime.now().replace(hour=23, minute=0, second=0)
    return (today_night - datetime.datetime.now()).seconds


def _get_second_from_now_to_friday_night():
    friday_night = datetime.datetime.now().replace(hour=23, minute=0, second=0)
    FRIDAY = 4
    while friday_night.weekday() != FRIDAY:
        friday_night += datetime.timedelta(days=1)
    return (friday_night - datetime.datetime.now()).seconds


def _finalize_add_reminder(bot, job_queue, chat_data):
    chat_id = chat_data.pop('chat_id')
    period = chat_data.pop('period')
    message = chat_data.pop('message')
    number_of_seconds_in_one_day = 60 * 60 * 24

    if period == u'daily':
        interval = number_of_seconds_in_one_day
        first_time = _get_seconds_from_now_to_night()
    elif period == u'weekly':
        interval = number_of_seconds_in_one_day * 7
        first_time = _get_second_from_now_to_friday_night()
    else:
        bot.send_message(chat_id=chat_id, text='can\'t find this period')
        return

    job = job_queue.run_repeating(_reminder,
                                  interval=interval, first=first_time,
                                  context={'chat_id': chat_id, 'text': message})
    if not chat_data.get('jobs'):
        chat_data['jobs'] = []
    chat_data['jobs'].append(job)


def start(_bot, update):
    """Send a message when the command /start is issued."""
    start_message = 'Hi\nuse /add for add retro reminder'
    update.message.reply_text(start_message)


def start_add_reminder(bot, update, chat_data):
    chat_id = update.message.chat_id
    chat_data['chat_id'] = update.message.chat_id
    bot.send_message(text='Please send your preferred frequency of '
                     'this retro reminder.\n choose daily or weekly.',
                     chat_id=chat_id)
    return PERIOD_STATE


def get_reminder_period(bot, update, chat_data):
    chat_id = update.message.chat_id
    chat_data['period'] = update.message.text
    bot.send_message(text='Please send your retro reminder message',
                     chat_id=chat_id)
    return MESSAGE_STATE


def get_reminder_message_and_finalize_add_reminder(bot, update, job_queue,
                                                   chat_data):
    chat_data['message'] = update.message.text
    _finalize_add_reminder(bot, job_queue, chat_data)
    return ConversationHandler.END


def cancel(bot, update):
    chat_id = update.message.chat_id
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    bot.send_message(text='retro reminder addition canceled', chat_id=chat_id)
    return ConversationHandler.END


def delete(bot, update, chat_data):
    chat_id = update.message.chat_id
    jobs = chat_data.pop('jobs')
    for job in jobs:
        job.schedule_removal()
    bot.send_message(text='All reminder messages has been deleted',
                     chat_id=chat_id)


def error(_bot, update, error_):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error_)
