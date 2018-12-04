from flask import session, jsonify,render_template,current_app,abort,g,request
from info import models, db
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import news_blue


@news_blue.route('/news_collect',methods=["POST"])
@user_login_data
def news_collect():
    """
    #收藏选项:
    0.参数：1.用户 2.新闻id  3.收藏类型 (未收藏,已收藏)
    1.接受参数
    2.效验参数 是否都不为空
    3.判断类型,如未收藏进行收藏,如已收藏取消收藏
    4.返回结果
    :return:

    """
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="请先进行登陆")

    news_id = request.json.get("news_id")
    collect_type = request.json.get("action")

    if not all([news_id,collect_type]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")

    if not collect_type in ["collect","cancel_collect"]:
        return jsonify(errno=RET.PARAMERR,errmsg="收藏参数不正确!")

    try:
        news = models.News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据失败!")

    if not news:
        return jsonify(errno=RET.NODATA,errmsg="无新闻数据")

    try:
        if collect_type == "collect":
            if not news in g.user.collection_news:
                g.user.collection_news.append(news)
        else:
            if news in g.user.collection_news:
                g.user.collection_news.remove(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="设置收藏错误!")

    return jsonify(errno=RET.OK,errmsg="添加收藏成功!")


@news_blue.route('/<int:num>')
@user_login_data
def news_item(num):
    # session_id = session.get("user_id")
    # # print (session_id)
    # user = None
    # if session_id:
    #     try:
    #         # user = models.User.query.filter(models.User.id == session_id).first()
    #         user = models.User.query.get(session_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    #         return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    # 使用num查询新闻信息
    news = None
    try:

        # print(type(num))
        # news = models.News.query.filter(models.News.id == num).first()
        news = models.News.query.get(num)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    if not news:
        abort(404)

    # news_list= [ ]
    # news_list.append(news.to_dict())
    # 放入列表中是为了在模板中方便遍历,并不是所有数据都需要放入列表中！！！
    # print(news_list)
    # print (user)

    #热门数据
    try:
        news_list = models.News.query.order_by(models.News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    n_news_list = [ ]
    for item in news_list:
        n_news_list.append(item.to_dict())

    #查询用户是否有收藏
    is_collected = False
    if g.user and news in g.user.collection_news:
        is_collected = True

    data = {
        "user_info":g.user.to_dict() if g.user else "" ,#else 后面添加的需要是None 并不能是 “ ”这样表明是一个空格
        "news_info":news.to_dict(),
        "n_news_list" :n_news_list,
        "is_collected":is_collected
    }

    return render_template("news/detail.html",data=data)