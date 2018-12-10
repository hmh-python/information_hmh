from datetime import timedelta
import datetime
from flask import render_template,request, jsonify,current_app,session,redirect,g
import time

from info import constants, db
from info import models
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import admin_blue

#新闻审核详情
@admin_blue.route('/news_review_detail',methods=["GET","POST"])
@user_login_data
def news_review_detail():

    if request.method == "GET":
        news_id = request.args.get("news_id")

        # print (news_id)
        if not news_id:
            return render_template('admin/news_review_detail.html', errmsg="参数错误!")

        try:
            news_item = models.News.query.get(news_id)
            # news_item = models.News.query.filter(models.News.id == news_id).first()
            # print (news_item)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/news_review_detail.html',errmsg="查询数据库中新闻失败!")

        return render_template('admin/news_review_detail.html',data = news_item.to_dict())

    news_id = request.json.get("news_id")
    action = request.json.get("action")
    reason = request.json.get("reason")  #如不通过标注不通过理由

    if not all ([news_id,action]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误!")
    if not action in ['reject','accept']:
        return jsonify(errno=RET.PARAMERR,errmsg="参数类型错误!")
    if action == "accept":
        try:
            news = models.News.query.get(news_id)
            news.status = 0
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="数据库操作失败!")
    else:
        try:
            news = models.News.query.get(news_id)
            news.status = -1
            news.reason = reason
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="数据库操作失败!")
    return jsonify(errno=RET.OK,errmsg="数据库操作成功!")

#新闻审核展示
@admin_blue.route('/news_review',methods=["GET"])
@user_login_data
def news_review():

    page = request.args.get('p','1')
    content = request.args.get("content")
    try:
        page = int(page)
    except Exception as e:
        page = 1

    sel_list = [models.News.status != '0']
    if content:
        sel_list.append(models.News.title.contains(content))
    try:
        paginate = models.News.query.filter(*sel_list).paginate(page,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据库失败!")
    currentPage = paginate.page
    totalPage = paginate.pages
    items = paginate.items
    # print (items)

    new_rev_list = []
    for new in items:
        new_rev_list.append(new.to_review_dict())
    # print (new_rev_list)
    data = {
        "currentPage" :currentPage,
        "totalPage" : totalPage,
        "news_item" : new_rev_list
    }

    return render_template('admin/news_review.html',data=data)

    # content = request.form.get("content")
    # # print (content)
    # try:
    #     paginate = models.News.query.filter(models.News.status != '0',models.News.title.contains(content)).paginate(1,constants.ADMIN_NEWS_PAGE_MAX_COUNT,False)
    #
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return render_template('admin/news_review.html', errmsg="查询数据库失败!")
    #
    # currentPage = paginate.page
    # totalPage = paginate.pages
    # items = paginate.items
    #
    # news_item = []
    # for item in items:
    #     news_item.append(item.to_review_dict())
    #     # print (item.to_dict())
    #
    # data = {
    #     "currentPage": currentPage,
    #     "totalPage": totalPage,
    #     "news_item": news_item
    # }
    # return render_template('admin/news_review.html',data=data)


#用户管理--用户列表
@admin_blue.route('/user_list')
@user_login_data
def user_list():

    page = request.args.get('p','1')

    try:
        page = int(page)
    except Exception as e:
        page = 1

    try:
        paginate = models.User.query.filter(models.User.is_admin == False).order_by(models.User.create_time.desc()).paginate(page,9,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/user_list.html',errmsg="查询数据库失败!")

    current_page = paginate.page
    totl_page = paginate.pages
    user_item = paginate.items

    us_list = []
    for item in user_item:
        us_list.append(item.to_admin_dict())

    data = {
        "currentPage" :current_page,
        "totlPage" : totl_page,
        "us_list" :us_list
    }

    return render_template('admin/user_list.html',data=data)


#用户管理---用户统计
@admin_blue.route('/user_count')
@user_login_data
def user_count():

    #全部人数除管理员
    try:
        user_sum = models.User.query.filter(models.User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    #当月活人数
    local_time = time.localtime()
    mon_str = "%d-%d-1"%(local_time.tm_year,local_time.tm_mon)
    mon_ob = datetime.datetime.strptime(mon_str,'%Y-%m-%d')
    try:
        user_mon = models.User.query.filter(models.User.last_login>mon_ob,models.User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    #日活人数
    local_time = time.localtime()
    day_str = "%d-%d-%d" % (local_time.tm_year,local_time.tm_mon,local_time.tm_mday)
    mon_ob = datetime.datetime.strptime(day_str, '%Y-%m-%d')
    try:
        user_day = models.User.query.filter(models.User.last_login > mon_ob, models.User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询失败!")


    #用户登陆活跃数
    date_list = []
    user_list = []
    for i in range(0,15):

        start_date = mon_ob - timedelta(days=i)

        end_date = mon_ob - timedelta(days=i-1)

        date_list.append(start_date.strftime('%m-%d'))

        user_date = models.User.query.filter(models.User.last_login>=start_date,models.User.last_login<=end_date,models.User.is_admin == False).count()
        # print(user_date)
        user_list.append(user_date)

    date_list.reverse()
    user_list.reverse()

    data = {
        "user_sum":user_sum,
        "user_mon":user_mon,
        "user_day":user_day,
        "date_list" :date_list,
        "user_list" :user_list
    }


    return render_template('admin/user_count.html',data=data)


@admin_blue.route('/index')
@user_login_data
def index():

    return render_template('admin/index.html',user_info=g.user.to_dict())


@admin_blue.route('/login',methods=['GET','POST'])
def login():

    if request.method == "GET":

        if session.get("is_admin"):
            return redirect('/admin/index')

        return render_template("admin/login.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if not all ([username,password]):
        return render_template("admin/login.html",errno=RET.PARAMERR,errmsg="参数不全!")

    try:
        user = models.User.query.filter(models.User.mobile == username,models.User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")
    if not user:
        return jsonify(errno=RET.NODATA,errmsg="管理员不存在!")

    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR,errmsg="密码错误!")

    session["user_id"] = user.id
    session["username"] = username
    session["mobile"] = user.mobile
    session["is_admin"] = user.is_admin

    return redirect('/admin/index')

