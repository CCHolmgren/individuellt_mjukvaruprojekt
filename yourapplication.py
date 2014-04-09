from flask import Flask, render_template
#from flask.ext.sqlalchemy import SQLAlchemy
from ApplicationModel import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:bubblegum123@localhost/postgres'
#db = SQLAlchemy(app)
db.init_app(app)

@app.route('/')
def index():
    return render_template('main.html',message='Hej meddelande')

if __name__ == '__main__':
    app.run()