from flask import Flask, render_template, g, request, flash, redirect, url_for
from model.database import db
from model.model import User
from model.Forms import RegistrationForm

app = Flask(__name__)
app.secret_key = "Wtf is wrong with you? Why won't you just let me register a user sometime today? :("
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
db.init_app(app)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        return render_template('main.html',message='Du accessade sidan med post istället för get')
    if request.method == 'GET':
        return render_template('main.html',message='Du accessade sidan med get istället för post')

@app.route('/register', methods=['GET','POST'])
def register():
    print('you were here')
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            user = User(form.username.data, form.email.data, *encrypt(form.password.data))
            db.session.add(user)
            db.session.commit()
            flash("Thanks for registering")
            return redirect(url_for('index'))
        except Exception:
            flash('Something horrible happened')
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
