from flask import Flask, render_template, g, request
from model.database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
db.init_app(app)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        return render_template('main.html',message='Du accessade sidan med post istället för get')
    if request.method == 'GET':
        return render_template('main.html',message='Du accessade sidan med get istället för post')

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
    #print(sha512("what"))
    app.run()
