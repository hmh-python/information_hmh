from info import db
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from . import user_blue
from flask import render_template,g,redirect,request, jsonify,current_app


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

    return jsonify(errno=RET.OK,errmsg="修改内容成功！")

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
