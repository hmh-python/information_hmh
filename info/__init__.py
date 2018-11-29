from flask import Flask
from Config import Config_dict
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import  CSRFProtect
from flask_session import Session


def curren_app():

    app = Flask(__name__)

    app.config.from_object(Config_dict["Product"])

    db = SQLAlchemy(app)

    CSRFProtect(app)

    Session(app)

    return app