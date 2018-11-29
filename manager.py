from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import  CSRFProtect
from redis import StrictRedis
from flask_session import Session
from datetime import timedelta


app = Flask(__name__)

app.config["SECRET_KEY"] = "qawsedrf"

app.config["SQLALCHEMY_DATABASE_URI"]="mysql+pymysql://root:mysql@localhost:3306/information_hmh"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db = SQLAlchemy(app)

redis_info = StrictRedis(host="localhost",port=6379)

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_REDIS"] = StrictRedis(host="localhost",port=6379)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=2)


CSRFProtect(app)

Session(app)

@app.route('/')
def index():

    return ('hello word!')

if __name__ == '__main__':
    app.run()