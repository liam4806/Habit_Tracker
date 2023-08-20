from routes import pages
from flask import Flask
import sys
from pymongo import MongoClient


app = Flask(__name__)
app.register_blueprint(pages)
client=MongoClient("MongoDBURLhere")
app.db=client.tracker
app.secret_key = 'super secret key'
app.config['SESSION_TYPE']='filesystem'
