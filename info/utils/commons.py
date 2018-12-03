#公共函数
from functools import wraps

from flask import session, current_app, g


#使用过滤器,过滤颜色提示
def  index_class(index):
    if index == 1:
        return "first"
    elif index == 2 :
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""

def user_login_data(index_func):
    @wraps(index_func)
    def warpper(*args,**kwargs):
        session_id = session.get("user_id")
        user = None
        if session_id:
            try:
                from info import models
                user = models.User.query.get(session_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return index_func(*args,**kwargs)
    return warpper