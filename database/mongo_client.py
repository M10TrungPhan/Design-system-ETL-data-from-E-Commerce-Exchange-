import pymongo

from config.config import Config


class MongoDatabase:
    def __init__(self):
        self.config = Config()
        self.host = self.config.mongodb_host
        self.port = self.config.mongodb_port
        self.username = self.config.mongodb_username
        self.password = self.config.mongodb_password
        self.client = pymongo.MongoClient(host=self.host, port=self.port, username=self.username,
                                          password=self.password)

