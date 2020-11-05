import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineQueryResultLocation
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from telegram.utils.helpers import escape_markdown

import json

from conf.settings import BASE_API_URL, TELEGRAM_TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    response_message = """
    Comandos disponíveis:
    /http <status HTTP>
    
    Você também pode enviar a localização para o bot"""
    context.bot.sendMessage(
        chat_id=update.effective_chat.id,
        text=response_message
    )

def http_cats(update, context):
    context.bot.sendPhoto(
        chat_id=update.effective_chat.id,
        photo=BASE_API_URL + context.args[0]
    )

def location(update, context):
    """
    docstring
    """
    print(update)
    if update.edited_message:
        print("Mensagem atualizada de", update.edited_message.from_user.first_name, update.edited_message.location.longitude, update.edited_message.location.latitude)
    else:
        print("Mensagem nova de", update.message.from_user.first_name, update.message.location.longitude, update.message.location.latitude)

def inlinequery(update, context):
    query = update.inline_query.query
    results = [
        InlineQueryResultLocation(id = uuid4(), 
                                  latitude = update.inline_query.location.latitude, 
                                  longitude = update.inline_query.location.longitude, title="Location")
    ]

    update.inline_query.answer(results)

def unknown(update, context):
    response_message = "Comando não reconhecido"
    context.bot.sendMessage(
        chat_id=update.effective_chat.id,
        text=response_message
    )

def main():
    updater = Updater(token=TELEGRAM_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(
        CommandHandler('start', start)
    )
    dispatcher.add_handler(
        CommandHandler('http', http_cats, pass_args=True)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.location, location)
    )
    dispatcher.add_handler(
        InlineQueryHandler(inlinequery)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.command, unknown)
    )

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()