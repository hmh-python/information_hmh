from info import models
from . import index_blue
from flask import render_template,current_app,session

@index_blue.route('/',methods=["GET","POST"])
def show_index():

    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = models.User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)


    data = {
        "user_info":user.to_dict() if user else ""

    }

    return render_template("news/index.html",data=data)

    # return ('hello word')

@index_blue.route('/favicon.ico')
def get_web_logo():

    return current_app.send_static_file("news/favicon.ico")
