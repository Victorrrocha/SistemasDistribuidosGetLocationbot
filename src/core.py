#Programa adapatado de https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py

import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineQueryResultLocation
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from telegram.utils.helpers import escape_markdown

from pymongo import MongoClient
import pymongo

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
    /my_location
    
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

def my_location(update, context):
    print(update)
    search = collection.find_one({"user_id": update.message.from_user.id})
    coord = search["geometry"]["coordinates"]
    response_message = f"Última localização: Long: {coord[0]} Lat: {coord[1]}"
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                            text=response_message)

def location(update, context):
    """
    docstring
    """
    print(update)
    if update.edited_message:
        print("Mensagem atualizada de", update.edited_message.from_user.first_name, update.edited_message.location.longitude, update.edited_message.location.latitude)
        user_location = {
            'user_id':   update.edited_message.from_user.id,
            'user_name': update.edited_message.from_user.first_name,
            "geometry": {
                "type": "Point",
                "coordinates": [update.edited_message.location.longitude, 
                                update.edited_message.location.latitude]
            }
            
        }
    else:
        print("Mensagem nova de", update.message.from_user.first_name, update.message.location.longitude, update.message.location.latitude)
        user_location = {
            'user_id':   update.message.from_user.id,
            'user_name': update.message.from_user.first_name,
            "geometry": {
                "type": "Point",
                "coordinates": [update.message.location.longitude, 
                                update.message.location.latitude]
            }
        }
    collection.replace_one(
        {"user_id": update.message.from_user.id}, 
        user_location, 
        upsert= True
    ) #insere se não existir
    

def inlinequery(update, context):
    # query = update.inline_query.query
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
        CommandHandler('my_location', my_location)
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
    print("Starting connection with database server")
    client = MongoClient('localhost', 27017) # making connection
    db = client.locations # getting database 'locations'
    collection = db.loc_collection # getting collection 'loc_collection'
    collection.create_index([("geometry", pymongo.GEOSPHERE)])

    print("press CTRL + C to cancel.")
    main()