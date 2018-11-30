from . import index_blue
from flask import render_template,current_app
from info import redis_store

@index_blue.route('/',methods=["GET","POST"])
def show_index():

    redis_store.set("name","laohe")
    print (redis_store.get("name"))


    return render_template("news/index.html")

    # return ('hello word')

@index_blue.route('/favicon.ico')
def get_web_logo():

    return current_app.send_static_file("news/favicon.ico")
