from redis import StrictRedis
from datetime import timedelta

class Config(object):

    SECRET_KEY = "qawsedrf"

    DEBUG = True

    #mysql配置文件
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql@localhost:3306/information_hmh"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #redis配置
    redis_host = "127.0.0.1"
    redis_port = 6379

    #Session配置文件
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = StrictRedis(host=redis_host,port=redis_port)
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)


class DevelopementConfig(Config):
    '''开发者模式'''
    DEBUG = True


class ProductionConfig(Config):
    '''生产者模式'''
    DEBUG = False

class TestingConfig(Config):
    '''测试者模式'''
    DEBUG = True


Config_dict = {
    "Develo" : DevelopementConfig,
    "Product" : ProductionConfig,
    "Test" : TestingConfig
}