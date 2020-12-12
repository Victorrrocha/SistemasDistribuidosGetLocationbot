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
import pymongo
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
        dlon = longitude_point - longitude_user
        dlat = latitude_point - latitude_user
        a = math.sin(dlat / 2)**2 + math.cos(latitude_user) * math.cos(latitude_point) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        if distance < menor:
            menor = distance
            name_point = i
    return name_point
    

def my_location(update, context):
    print(update)
    search = collection.find_one({"user_id": update.message.from_user.id})
    if(search == None):
        response_message = "Não foi encontrado sua localização. Envie sua localização ou tente novamente."
    else:
        coord = search["geometry"]["coordinates"]
        response_message = f"Última localização: Long: {coord[0]} Lat: {coord[1]}"
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=response_message)

def location(update, context):
    """
    docstring
    """
    print()
    print(update)
    user_id = ''
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
        user_id = update.edited_message.from_user.id
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
        user_id = update.message.from_user.id
    collection.replace_one(
        {"user_id": user_id}, 
        user_location, 
        upsert= True
    ) #insere se não existir, se existir ele substitui as informações
    

def inlinequery(update, context):
    # query = update.inline_query.query
    # results = [
    #     InlineQueryResultLocation(id = uuid4(), 
    #                               latitude = update.inline_query.location.latitude, 
    #                               longitude = update.inline_query.location.longitude, title="Sua localização")
    # ]
    
    res = calc_smaller_distance(update.inline_query.location.latitude, update.inline_query.location.longitude)
    results = [
        InlineQueryResultLocation(id = uuid4(), 
                                  latitude = points_lat_long[res][0], 
                                  longitude = points_lat_long[res][1], 
                                  title=res)
    ]
    
    # Código abaixo comentado para uso futuro
    # search = collection.find({
    #     "geometry": {
    #         "$nearSphere" : [update.inline_query.location.longitude, 
    #                          update.inline_query.location.latitude]
    #     }
    # })
    # a função find() retorna um objeto Cursor que é usado para iterar os resultados de uma query. Ao usá-lo para percorrer os resultados, não será possível usá-lo novamente. Use a função clone() caso use mais de uma vez antes do primeiro uso.
    # results = [InlineQueryResultLocation(id = uuid4(), 
    #                                      latitude  = i["geometry"]["coordinates"][0], 
    #                                      longitude = i["geometry"]["coordinates"][1], 
    #                                      title = i["user_name"]) for i in list(search)]
    update.inline_query.answer(results)
    print(update.inline_query)

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
    
    print([i for i in collection.find()])

    print("press CTRL + C to cancel.")
    main()