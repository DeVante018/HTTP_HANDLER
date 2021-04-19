# I will use this class to treat variable as if they are static
# also will setup my database here so it is accessible by all levels of the server
import pymongo

connection = pymongo.MongoClient("mongodb://my_database:27017")
data_base = connection["CSE312"]
chat_collection = data_base["chat_log"]


class Statics:
    chat = chat_collection
    captions_images = []
    server_clients = []
    server_web_sockets = []