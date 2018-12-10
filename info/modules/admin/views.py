from datetime import timedelta
import datetime
from flask import render_template,request, jsonify,current_app,session,redirect,g
import time
from info import models
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import admin_blue

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

