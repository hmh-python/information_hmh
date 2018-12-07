import logging
from logging.handlers import RotatingFileHandler
from flask import Flask,render_template,g
from Config import Config_dict
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_session import Session
from redis import StrictRedis
from info.utils.commons import user_login_data

db = SQLAlchemy()

redis_store = None

def curren_app(config_name):

    app = Flask(__name__)

    curtten_config = Config_dict.get(config_name)

    app.config.from_object(curtten_config)

    myloggin(curtten_config.LEVELNAME)

    db.init_app(app)

    global redis_store
    redis_store = StrictRedis (host=curtten_config.redis_host,port=curtten_config.redis_port,decode_responses=True)

    Session(app)

    CSRFProtect(app)

    from info.modules.index import index_blue
    app.register_blueprint(index_blue)


    from info.modules.passport import passport_bule
    app.register_blueprint(passport_bule)

    @app.after_request
    def at_request(resp):
        csrf_token = generate_csrf()
        resp.set_cookie("csrf_token",csrf_token)
        return resp

    @app.errorhandler(404)
    @user_login_data
    def page_not_found(e):

        data = {
            "user_info" : g.user.to_dict() if g.user else ""
        }

        return render_template("news/404.html",data=data)

    from info.modules.news import news_blue
    app.register_blueprint(news_blue)

    from info.utils.commons import  index_class
    app.add_template_filter(index_class,"index_class")

    from info.modules.porfile import user_blue
    app.register_blueprint(user_blue)

    print(app.url_map)
    return app



def myloggin(levelname):

    # 设置日志的记录等级
    logging.basicConfig(level=levelname)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

