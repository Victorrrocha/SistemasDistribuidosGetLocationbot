#Programa adapatado de https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py

import logging
import math
import pymongo
import json
from uuid import uuid4
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineQueryResultLocation
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from telegram.utils.helpers import escape_markdown
from pymongo import MongoClient
from conf.settings import BASE_API_URL, TELEGRAM_TOKEN


points_lat_long = {"Garimpeiro": [2.820486,-60.671979], "portalMilenio":[2.824720, -60.676921]}

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

def calc_smaller_distance(latitude, longitude):
    R = 6373.0
    latitude_user   = math.radians(latitude)
    longitude_user  = math.radians(longitude)
    menor = 999999999

    for i in points_lat_long:
        latitude_point   = math.radians(points_lat_long[i][0])
        longitude_point  = math.radians(points_lat_long[i][1])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        if distance < menor:
            menor = distance
            name_point = i
    return name_point
    

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
    ) #insere se não existir, se existir ele substitui as informações
    

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
    collection.create_index([("geometry", pymongo.GEOSPHERE)]) #create 2dsphere index

    print("press CTRL + C to cancel.")
    main()