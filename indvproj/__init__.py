from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
import flask_sqlalchemy

print("Here?")
app = Flask(__name__)
print("Here?")

app.secret_key = "Wtf is wrong with you? Why won't you just let me register a user sometime today? :("
print("Here?")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
print("Here?")

flask_sqlalchemy.SQLAlchemy()
print("But not here?")
db = flask_sqlalchemy.SQLAlchemy()
db.init_app(app)
print("But not here then?")
db_session = db.session