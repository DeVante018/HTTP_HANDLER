# I will use this class to treat variable as if they are static
# also will setup my database here so it is accessible by all levels of the server
import pymongo

connection = pymongo.MongoClient("mongodb://localhost:27017")
data_base = connection["CSE312"]
chat_collection = data_base["chat_log"]
cookies_collection = data_base["cookies"]
usernames_passwords = data_base["users"]
authorization_tokens = data_base["authorized"]


class Statics:
    token = ""
    current_cookie = ""
    chat = chat_collection
    db_cookies = cookies_collection  # Oreo's, ChipsAhoy, Pringles, ect
    usr_pwd = usernames_passwords
    auth = authorization_tokens
    captions_images = []
    server_clients = []
    server_web_sockets = []
