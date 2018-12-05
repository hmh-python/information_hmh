from flask import session, jsonify,render_template,current_app,abort,g,request
from info import models, db
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import news_blue


#添加评论
@news_blue.route('/news_comment',methods=["POST"])
@user_login_data
def news_comment():
    """
    添加评论
    1.接受参数 user_id,news_id,comment_contents,parent_id
    1.1判断用户是否为空
    2.效验参数 空效验
    3.查看新闻是否存在
    4.查看是否有父类评论
    5.把评论添加到数据库
    6.返回成功信息
    :return:
    """
    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg="用户未登录")

    news_id = request.json.get("news_id")
    comment_con = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    if not all ([news_id,comment_con]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误!")
    try:
        news = models.News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")
    if not news:
        return jsonify(errno=RET.NODATA,errmsg="该新闻不存在!")

    comment = models.Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = comment_con

    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR,errmsg="数据库插入报错")

    data = comment.to_dict()

    return jsonify(errno=RET.OK,errmsg="评论加入成功.",data=data)

#点击进行收藏
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

    #添加评论信息至前端
    try:
        comment = models.Comment.query.filter(models.Comment.news_id==num).order_by(models.Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询错误!")

    #查看评论计数

    comment_list = []
    for item in comment:
        comment_list.append(item.to_dict())

    #查询评论内容
    # comment_list = models.Comment.query.filter(models.Comment.news_id==news.id).all()
    #
    # new_com_list = [ ]
    # for comment in comment_list:
    #     new_com_list.append(comment.to_dict())


    data = {
        "user_info":g.user.to_dict() if g.user else "" ,#else 后面添加的需要是None 并不能是 “ ”这样表明是一个空格
        "news_info":news.to_dict(),
        "n_news_list" :n_news_list,
        "is_collected":is_collected,
        "comment_list" :comment_list,
    }

    return render_template("news/detail.html",data=data)