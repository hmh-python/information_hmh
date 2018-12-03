from flask import session, jsonify,render_template,current_app
from info import models
from info.utils.response_code import RET
from . import news_blue

@news_blue.route('/<int:num>')
def news_item(num):
    session_id = session.get("user_id")
    # print (session_id)
    user = None
    if session_id:
        try:
            # user = models.User.query.filter(models.User.id == session_id).first()
            user = models.User.query.get(session_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    # 使用num查询新闻信息
    try:

        # print(type(num))
        # news = models.News.query.filter(models.News.id == num).first()
        news = models.News.query.get(num)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    # news_list= [ ]
    # news_list.append(news.to_dict())
    # 放入列表中是为了在模板中方便遍历,并不是所有数据都需要放入列表中！！！
    # print(news_list)
    # print (user)

    #热门数据
    try:
        news_list = models.News.query.order_by(models.News.create_time.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    n_news_list = [ ]
    for item in news_list:
        n_news_list.append(item.to_dict())

    data = {
        "user_info":user.to_dict() if user else "" ,#else 后面添加的需要是None 并不能是 “ ”这样表明是一个空格
        "news_info":news.to_dict(),
        "n_news_list" :n_news_list
    }

    return render_template("news/detail.html",data=data)