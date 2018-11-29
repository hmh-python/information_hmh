from redis import StrictRedis
from datetime import timedelta

class Config(object):

    SECRET_KEY = "qawsedrf"

    #mysql配置文件
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql@localhost:3306/information_hmh"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #Session配置文件
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = StrictRedis(host="localhost",port=6379)
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)