import json
from pymongo import MongoClient
import pickle
# from flask import Flask, request, jsonify
import time

class Collection:
    def __init__(self, uri):
        self.uri = uri
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=60000)
    
    def get_db(self, name):
        return self.client['EEIoT_newbie']

    def get_collection(self, name):
        db = self.get_db('EEIoT_newbie')
        return db[name]

# uri = "mongodb+srv://EEIoT_newbie:ILOVEAIFOREVER@cluster0.xolr95j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

if __name__ == "__main__":
    collection = Collection("mongodb+srv://EEIoT_newbie:ILOVEAIFOREVER@cluster0.xolr95j.mongodb.net/").get_collection('frames')
   