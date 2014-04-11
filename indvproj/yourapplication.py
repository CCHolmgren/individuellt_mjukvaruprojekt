from flask import Flask, render_template
from model.database import db
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
db.init_app(app)

@app.route('/')
def index():
    return render_template('main.html',message='Hej meddelande')

def sha512(something):
    import os
    something = something.encode('utf-8')
    salt = os.urandom(24)
    return hashlib.sha512(something + salt).hexdigest(),salt

if __name__ == '__main__':
    #print(sha512("what"))
    app.run()
