from flask import Flask
from flask_sqlalchemy import SQLAlchemy
#from model import *
#import flask_sqlalchemy


app = Flask(__name__)
app.secret_key = "Wtf is wrong with you? Why won't you just let me register a user sometime today? :("
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:thisisapassword@localhost/postgres'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'

db = SQLAlchemy(app)
db_session = db.session
