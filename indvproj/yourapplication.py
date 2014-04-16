from flask import Flask, render_template, g, request, flash, redirect, url_for
from database import db_session
from models import User, Post
from forms import RegistrationForm, NewPostForm
from flask_login import LoginManager
from flask.ext.login import login_user, login_required
import _datetime

app = Flask(__name__)
app.secret_key = "Wtf is wrong with you? Why won't you just let me register a user sometime today? :("
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/')
def index():
    #print(Post.query.limit(10).all())
    return render_template('main.html',message='Du accessade sidan med get istället för post',posts=Post.query.limit(10).all())

@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    form = NewPostForm(request.form)
    if request.method == 'POST' and form.validate():
        #try:
        #def __init__(self, createdby, timeposted, content, typeid, title):
        post = Post(5,_datetime.datetime.now(),form.content.data,1,form.title.data)
        print(post)
        db_session.add(post)
        db_session.commit()
        redirect(url_for("index"))
        #except Exception:
        #    flash('Something horrible happened')
        #    print('Damn')
        #    redirect(url_for("new_post"))
    return render_template('new_post.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    print('you were here')
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            user = User(form.username.data, form.email.data, *encrypt(form.password.data))
            db_session.add(user)
            db_session.commit()
            login_user(user)
            flash("Thanks for registering")
            return redirect(url_for('index'))
        except Exception as e:
            flash('Something horrible happened')
            print(e)
            redirect(url_for("register"))
    return render_template('create_user.html', form=form)

def encrypt(password):
    """
    Takes a password, encodes it in utf-8 and
    then uses the haslib sha512 function to encrypt it.
    The hexdigest and the salt used is then returned.
    """

    import os
    import hashlib
    password = password.encode('utf-8')
    salt = os.urandom(24)
    return hashlib.sha512(password + salt).hexdigest(),salt

if __name__ == '__main__':
    print("Encrypting 'what' and returns the sha512 hash with the salt generated",encrypt("what"))
    app.debug = True
    app.run()
