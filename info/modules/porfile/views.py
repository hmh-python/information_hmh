from info import db,constants
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import user_blue
from flask import render_template,g,redirect,request, jsonify,current_app
from info.utils.image_storage import image_stor


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
