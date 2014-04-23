from flask import Flask, g
from database import db_session, db
from models import User
from flask_login import current_user
from loginmanager import login_manager
from views import MainView, RegisterView, PostView, LoginView, UserView, CollectionView
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)
app.secret_key = "Wtf is wrong with you? Why won't you just let me register a user sometime today? :("
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'

csrf = CsrfProtect()

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'LoginView:index'
csrf.init_app(app)

MainView.register(app)
RegisterView.register(app)
PostView.register(app)
LoginView.register(app)
UserView.register(app)
CollectionView.register(app)


@app.before_request
def before_request():
    g.user = current_user


@app.errorhandler(404)
def page_not_found(e):
    return "Sorry, the page that you equested could not be found. {} {}".format(dir(e), e)


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
