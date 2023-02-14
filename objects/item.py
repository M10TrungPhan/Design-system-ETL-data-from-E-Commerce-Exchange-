import hashlib

# from config.config import Config


class Item:

    def __init__(self, data_package_item: dict):
        self.data_package_item = data_package_item
        # self.config = Config()

    @classmethod
    def class_name(cls):
        return cls.__name__


