#Programa adapatado de https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinebot.py

import logging
import math
import pymongo
import json
from uuid import uuid4
from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, InlineQueryResultLocation
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext, CommandHandler, Filters, MessageHandler, Updater
from telegram.utils.helpers import escape_markdown

import twitter

from pymongo import MongoClient
import pymongo
from conf.settings import BASE_API_URL, TELEGRAM_TOKEN,TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET, TWITTER_CONSUMER_TOKEN_KEY, TWITTER_CONSUMER_TOKEN_SECRET
from bson.objectid import ObjectId
from datetime import datetime

twtApi = twitter.Api(TWITTER_CONSUMER_TOKEN_KEY, TWITTER_CONSUMER_TOKEN_SECRET,TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)

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
    /dig
    
    Você também pode enviar a localização para o bot"""
    context.bot.sendMessage(
        chat_id=update.effective_chat.id,
        text=response_message
    )

def comecar_partida(update, context):
    print(update)
    partida_collection.update_one({
        "id_host": update.message.from_user.id
    },{
        "$set": {
            "id_host": update.message.from_user.id,
            "nome_host": update.message.from_user.first_name,
            "state": "ESPERANDO_LOCAL"
        }
    }, upsert=True)
    partida = partida_collection.find_one({"id_host": update.message.from_user.id})
    print(partida)
    context.bot.sendMessage(
        chat_id=update.effective_chat.id,
        text="O ID da partida é "+str(partida["_id"])
    )

def enviar_localizacao(update, context):
    """
    1) Tenta inserir na coleção de partidas
    2)
    """
    if update.edited_message:
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
        user_location = {
            'user_id':   update.message.from_user.id,
            'user_name': update.message.from_user.first_name,
            "geometry": {
                "type": "Point",
                "coordinates": [update.message.location.longitude, 
                                update.message.location.latitude]
            }
        }
    partida = partida_collection.find_one({"id_host": user_location['user_id']})
    if(partida != None):
        if(partida["state"] == "ESPERANDO_LOCAL"):
            partida_collection.update_one({
                "id_host": user_location['user_id']
            },
            { 
                "$set": {
                    "local_tesouro": user_location["geometry"],
                    "state": "PRONTO",
                    "horario_enterro": datetime.utcnow()
                }
            })
    else:
        jogador = jogadores_collection.update_one({
            "id_jogador": user_location['user_id']
        },
        {   "$set": {
                "local_jogador": user_location["geometry"]
            }
        })

def novo_jogador(update, context):
    partida = partida_collection.find_one({"id_host": update.message.from_user.id})
    if(partida == None): #se ele não tiver como host
        if(len(context.args) == 0): return
        partida = partida_collection.find_one({"_id": ObjectId(context.args[0])})
        if(partida == None): return
        jogadores_collection.update_one({
            "id_jogador": update.message.from_user.id
        },
        {
            "$set": {
                "id_jogador": update.message.from_user.id,
                "nome_jogador": update.message.from_user.first_name,
                "id_partida": context.args[0],
                "escavacoes": 0
            }
        }, upsert=True)

def dig(update, context):
    print(update)
    search = jogadores_collection.find_one({"id_jogador": update.message.from_user.id})
    print(search)
    if(search == None):
        response_message = "Usuário não encontrado. Use o comando /novo_jogador."
    else:
        if ("local_jogador" not in search.keys()):
            response_message = "Você não tem localização salva, por favor envie sua localização."
        else:
            coord = search["local_jogador"]["coordinates"]

            #calculando distancia entre jogador e os premios
            resultado = partida_collection.aggregate([{
                "$geoNear": {
                    "near": coord,
                    "spherical": True,
                    "distanceField": "dist_calculated",
                    "query": {"_id": ObjectId(search["id_partida"])}
                }
            }])
            print(resultado)

            resultado = list(resultado)[0]

            response_message = "Tis cold as da Artic here ye scurvy dog! Do ye wish ta walk da plank?! Find us da tresure!"

            if(resultado["dist_calculated"] < 1000):
                response_message = "AHOY LASS! Yer just found mah tresure! Suas Coord => Long: {} Lat: {}".format(coord[0], coord[1])
                position = "google.com/maps/@{},{},21z".format(coord[0], coord[1])
                twtApi.PostUpdate("A seadog has fund a treasure {}".format(position))
            else:
                response_message = "Attention mate! I can smell da tresure! Keep yer eys open. U are {} of distance".format(resultado["dist_calculated"])
                jogadores_collection.update_one({
                    "id_jogador": update.message.from_user.id
                }, {
                    "$inc": {
                        "escavacoes": 1
                    }
                })
    context.bot.sendMessage(chat_id=update.effective_chat.id,
                                text=response_message)

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
        CommandHandler('comecar_partida', comecar_partida)
    )
    dispatcher.add_handler(
        MessageHandler(Filters.location, enviar_localizacao)
    )
    dispatcher.add_handler(
        CommandHandler('novo_jogador', novo_jogador, pass_args=True)
    )
    dispatcher.add_handler(
        CommandHandler('marco', dig)
    )

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    print("Starting connection with database server")
    print("Testando saída de texto do programa")
    client = MongoClient('mongodb://root:030596victor@mongo:27017') # making connection
    db = client.locations # getting database 'locations'
    collection = db.loc_collection # getting collection 'loc_collection'
    collection.create_index([("geometry", pymongo.GEOSPHERE)]) #create 2dsphere index
    partida_collection = db.partida_collection
    partida_collection.create_index([("local_tesouro", pymongo.GEOSPHERE)])
    jogadores_collection = db.jogadores_collection
    jogadores_collection.create_index([("local_jogador", pymongo.GEOSPHERE)])
    
    print([i for i in collection.find()])

    print("press CTRL + C to cancel.")
    main()