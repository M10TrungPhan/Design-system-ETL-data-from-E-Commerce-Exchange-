from database.mongo_client import MongoDatabase
from config.config import Config


class DatabaseShopee:
    def __init__(self):
        self.config = Config()
        self.mongodb = MongoDatabase()
        self.database = self.mongodb.client[self.config.data_shopee_database]
        self.data_col = self.database[self.config.data_shopee_collection]

    def get_link_col(self):
        urls = [x['url'] for x in self.data_col.find({}, {"url": 1})]
        return urls

    def get_data_col(self):
        data = [x for x in self.data_col.find()]
        return data

    def save_data(self, data):
        self.data_col.insert_one(data)

