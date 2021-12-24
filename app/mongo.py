from flask_pymongo import PyMongo


class AppDatabase:
    def __init__(self, app, uri):
        self.db = PyMongo(app, uri).db

    def _get_collection(self, collection):
        return getattr(self.db, collection)

    def contains(self, collection, document):
        return self._get_collection(collection).find(document).count_documents() != 0

    def insert_one(self, collection, document):
        return self._get_collection(collection).insert_one(document)

    def find(self, collection, document=None):
        current_collection = self._get_collection(collection)
        return current_collection.find() if document is None else current_collection.find(document)

    def find_one(self, collection, document=None):
        current_collection = self._get_collection(collection)
        return current_collection.find_one() if document is None else current_collection.find_one(document)

    def update_one(self, collection, document, update):
        self._get_collection(collection).update_one(document, update)

