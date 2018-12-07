from info import db,constants,models
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import user_blue
from flask import render_template,g,redirect,request, jsonify,current_app
from info.utils.image_storage import image_stor

#新闻列表
@user_blue.route('/news_list',methods=["GET"])
@user_login_data
def news_list():

    """
    1.获取参数
    2.转换类型
    3.在数据库进行查询需要审核的新闻列表,分页查询
    4.返回信息
    :return:
    """
    page = request.args.get("p","1")

    try:
        page = int(page)
    except Exception as e:
        page = 1

    try:
        news_li = g.user.news_list.paginate(page,4,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败！")

    currentPage = news_li.page
    totalPage = news_li.pages
    news_pages_item = news_li.items

    news_li_new = [ ]
    for news in news_pages_item:
        news_li_new.append(news.to_review_dict())

    data = {
        "news_list" : news_li_new,
        "currentPage" : currentPage,
        "totalPage" : totalPage
    }


    return render_template('news/user_news_list.html',data=data)

#新闻发布
@user_blue.route('/news_release',methods=["GET","POST"])
@user_login_data
def news_release():

    if not g.user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")
    try:
        Category = models.Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据库失败!")

    if request.method == "GET":
        return render_template("news/user_news_release.html",data = Category)
    """
    1.form 表单提交 接受参数 title  digest  index_image  content category_id
    2.效验是否为空
    3.上传图像
    4.创建新闻对象
    5.将新闻放入数据库进行审核
    6.返回响应
    :return:
    """
    title = request.form.get("title")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")
    category_id = request.form.get("category_id")

    if not all ([title,digest,index_image,content,category_id]):
        return jsonify(errno=RET.NODATA,errmsg="参数不全")

    try:
        image_name = image_stor(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="访问七牛云失败!")

    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg="新闻图片不存在!")

    add_news = models.News()
    add_news.title = title
    add_news.source = g.user.nick_name
    add_news.digest = digest
    add_news.content = content
    add_news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    add_news.category_id = category_id
    add_news.user_id = g.user.id
    add_news.status = 1
    try:
        db.session.add(add_news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return  jsonify(errno=RET.DBERR,errmsg="访问数据库失败!")

    return jsonify(errno=RET.OK,errmsg="新闻发布成功!")

#显示用户收藏
@user_blue.route('/user_collection',methods=["GET"])
@user_login_data
def user_collection():

    if not g.user:
        return jsonify(errno=RET.PARAMERR,errmsg="用户未登录!")

    """
    1.接受参数 第几页 一页显示的行数
    2.效验参数 是否为空如为空设置默认值
    3.从数据库查询用户的收藏记录
    4.返回响应

    1.获取参数
    2.参数类型转换
    3.分页查询,每页10条
    4.取出分页对象属性,总页数,当前页,当前页对象列表
    5.拼接数据,渲染页面
    :return:
    """
    page = request.args.get("p", "1")

    try:
        page = int(page)
    except Exception as e:
        page = 1

    try:
        # comment_paginate = models.Comment.query.filter(models.Comment.user_id == g.user.id).paginate(page,7,False) 这是
        # 查询用户的评论并不是收藏
        collention_paginate = g.user.collection_news.order_by(models.News.create_time.desc()).paginate(page,5,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询失败!")

    page = collention_paginate.page
    pages = collention_paginate.pages
    comment_item = collention_paginate.items
    comment_list = []
    for com_item in comment_item:
        # print (com_item)
        comment_list.append(com_item.to_dict())

    data = {
        "currentPage":page,
        "totalPage" :pages,
        "comment_list" : comment_list
    }

    return render_template('news/user_collection.html',data=data)


#上传头像
@user_blue.route('/pic_info',methods=["GET","POST"])
@user_login_data
def pic_info():

    if not g.user:
        return jsonify(errno=RET.PARAMERR,errmsg="用户未登录!")

    if request.method == "GET":

        data = g.user.to_dict()
        # data["avatar_url"] = constants.QINIU_DOMIN_PREFIX + g.user.avatar_url

        return render_template("news/user_pic_info.html",data=data)

    """
    1.获取参数,用户,上传的图片
    2.效验图片是否不为空
    3.通过七牛云上传图片
    4.设置图片到用户对象 ！
    4.返回响应
    """

    image = request.files.get("avatar")

    if not image:
        return jsonify(errno=RET.NODATA,errmsg="无图片信息")

    try:
        image_name = image_stor(image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="七牛云访问错误")

    if not image_name:
        return jsonify(errno=RET.NODATA,errmsg="图片上传失败!")

    try:
        g.user.avatar_url = image_name
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="数据库修改失败!")

    avatar_url = constants.QINIU_DOMIN_PREFIX + image_name
    # print (avatar_url)
    data = {"avatar_url":avatar_url}

    return jsonify(errno=RET.OK,errmsg="图片设置成功",data=data )


#密码修改
@user_blue.route('/pass_info',methods=["GET","POST"])
@user_login_data
def pass_info():

    if request.method == "GET":
        return render_template("news/user_pass_info.html")


      # 1.判断请求方式 get 不需要传入参数,post需要传入参数
      # 2.接受参数, 原始密码 新密码
      # 3.效验参数 空效验
      # 4.查看原始密码是否正确
      # 4.1 判断新旧密码是否一致
      # 5.更新密码
      # 6.返回响应

    if not g.user:
        return jsonify(errno=RET.NODATA,errmsg="无用户登陆")

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all ([new_password,old_password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误!")

    if not g.user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR,errmsg="原密码错误!")

    if old_password == new_password:
        return jsonify(errno=RET.DATAERR,errmsg="新密码与原密码一致,请重新输入")

    g.user.password = new_password

    return jsonify(errno=RET.OK,ermsg="密码已更新!")


#基本资料
@user_blue.route('/base_info',methods=["GET","POST"])
@user_login_data
def base_info():

    """
    0.判断请求方式
    1.效验用户是否登陆
    2.获取参数 个人签名,用户昵称,性别
    3.效验数据 空效验
    4.查看数据库中是否有该用户
    5.返回响应
    :return:
    """

    if request.method == "GET":
        user = g.user.to_dict()
        return render_template("news/user_base_info.html",data=user)

    if not g.user:
        return jsonify(errno=RET.SESSIONERR,errmsg="用户未登录")

    signature = request.json.get("signature")
    nick_name = request.json.get("nick_name")
    gender = request.json.get("gender")

    if not all ([signature,nick_name,gender]):
        return jsonify(errno=RET.NODATA,errmsg="参数错误!")

    if not gender in ["MAN","WOMAN"] :
        return jsonify(errno=RET.DATAERR,errmsg="性别参数错误!")

    try:
        g.user.signature = signature
        g.user.nick_name = nick_name
        g.user.gender = gender
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库操作失败!")

    return jsonify(errno=RET.OK,errmsg="修改成功！")

#进入用户中心
@user_blue.route("/info")
@user_login_data
def user_info():

    if not g.user:
        return  redirect("/")

    user_info = g.user.to_dict()
    # user_info["avatar_url"] = constants.QINIU_DOMIN_PREFIX  + g.user.avatar_url

    data = {
        "user_info" :user_info
    }

    return render_template("news/user.html",data=data)
