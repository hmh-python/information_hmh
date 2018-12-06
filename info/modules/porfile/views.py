from info import db
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import user_blue
from flask import render_template,g,redirect,request, jsonify,current_app


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
    data = {
    "user_info" : g.user.to_dict()
    }

    return render_template("news/user.html",data=data)
