from flask import Flask, render_template, g, request, flash, redirect, url_for
from database import db_session, db
from models import User, Post
from forms import RegistrationForm, NewPostForm
from loginmanager import login_manager
from flask.ext.login import login_user, login_required
import _datetime
from views import MainView, RegisterView, PostView

app = Flask(__name__)
app.secret_key = "Wtf is wrong with you? Why won't you just let me register a user sometime today? :("
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
db.init_app(app)
login_manager.init_app(app)
MainView.register(app)
RegisterView.register(app)
PostView.register(app)

@app.errorhandler(404)
def page_not_found(e):
    return "Sorry, nothing could be found. {}".format(e)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.teardown_appcontext
def shutdown_session(self, exception=None):
    db_session.remove()

if __name__ == '__main__':
    #print("Encrypting 'what' and returns the sha512 hash with the salt generated",encrypt("what"))
    app.debug = True
    app.run()
