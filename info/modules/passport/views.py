from datetime import datetime
import random
import re
from flask import make_response,request,current_app, jsonify,json,session
from info import constants,redis_store,db
from info import models
from info.libs.yuntongxun.sms import CCP
from info.utils.response_code import RET
from . import passport_bule
from info.utils.captcha import captcha


#退出
@passport_bule.route('/logout',methods=["POST"])
def logout_index():
    """
    请求路径: /passport/logout
    请求方式: POST
    请求参数： 当点击退出的时候浏览器会把自带的session返回回来
    :return:
    """
    try:
        session.pop("user_id",None)
        session.pop("mobile",None)
        session.pop("nick_name",None)
        session.pop("is_admin",None)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="参数错误!")

    return jsonify(errno=RET.OK,errmsg="账号已退出!")

#登陆
@passport_bule.route('/login',methods=["POST"])
def login_index():
    """
    请求路径: /passport/login
    请求方式: POST
    请求参数: mobile,password
    返回值: errno, errmsg

    1.接受参数
    2.判断参数是否为空
    3.判断手机号是否存在(根据手机号查询用户对象)
    4.判断用户是否存在
    5.判断密码是否正确
    6.记录用户的登陆信息到session
    7.返回响应
    :return:
    """
    request_dict = request.get_json()
    mobile = request_dict.get("mobile")
    password = request_dict.get("password")

    if not all ([mobile,password]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不全")
    try:
        db_user = models.User.query.filter(models.User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询错误!")
    if not db_user:
        return jsonify(errno=RET.NODATA,errmsg="用户不存在,请注册!")
    if not db_user.check_passowrd(password):
        return jsonify(errno=RET.DATAERR,errmsg="密码错误,请重新输入!")
    if mobile == db_user.mobile and db_user.check_passowrd(password):
        session["user_id"] = db_user.id
        session["mobile"] = mobile
        session["nick_name"] = db_user.nick_name
        session["is_admin"] = db_user.is_admin
        db_user.last_login = datetime.now()

        return jsonify(errno=RET.OK,errmsg="登陆成功!")

#注册信息
@passport_bule.route('/register',methods=["POST"])
def register_index():
    """请求路径: /passport/register
        请求方式: POST
        请求参数: mobile, sms_code,password
        返回值: errno, errmsg

        1.获取参数
        2.检验参数,为空效验
        3.根据手机号取出redis中短信验证码
        4.短信验证码正确性
        5.检查密码是否符合要求
        6.查看数据库中是否有该用户
        7.把用户插入数据库中,完成注册
        8.返回相应

    """
    request_dict = request.get_json()
    mobile = request_dict.get("mobile")
    sms_code = request_dict.get("sms_code")
    password = request_dict.get("password")
    if not all([mobile,sms_code,password]):
        return jsonify(errno=RET.NODATA,errmsg="参数不能为空")
    try:
        redis_sms_code = redis_store.get("sms_code:%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库提取验证码失败!")

    if not redis_sms_code:
        return jsonify(errno=RET.NODATA,errmsg="验证码已过期!")

    if sms_code != redis_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="验证码不正确!")

    # if not re.match(r"(\d{6,13})|(\w{6,13})",password):
    #     return jsonify(errno=RET.DATAERR,errmsg="密码过于简单!")
    try:
        user = models.User.query.filter(models.User.nick_name==mobile).first()
        # print (user)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询数据错误!")
    if user:
        return jsonify(errno=RET.DATAEXIST,errmsg="账号已存在!")
    try:
        add_user = models.User()
        add_user.nick_name = mobile
        add_user.password = password
        add_user.mobile = mobile
        db.session.add(add_user)
        # db.session.commit()  设置了自动提交
        return jsonify(errno=RET.OK,errmsg="账号注册成功!")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库查询数据错误!")

#手机验证码
@passport_bule.route('/sms_code',methods=["POST"])
def sms_code():
    """请求路径: /passport/sms_code
    请求方式: POST
    请求参数: mobile, image_code,image_code_id
    返回值: errno, errmsg

    1.获取参数
    2.效验参数,为空效验
    3.验证手机号格式是否正常
    4.根据图片验证码编号,取出redis图片验证码
    5.判断redis中的图片验证码是否过期
    6.取出图片验证码并删除redis图片的验证码
    7.正确性效验,传入的图片验证码和redis是否一致
    8.正常生成短信验证码,调用CCP对象来发送短信
    9.判断短信是否发送成功
    10.保存短信验证码到redis
    11.返回发送状态
    :return:
    """
    # json_data  =  request.data
    # request_dict = json.loads(json_data)
    # request_dict = request.json

    request_dict = request.get_json()
    # print (request_dict)
    mobile = request_dict.get("mobile")
    image_code = request_dict.get("image_code")
    image_code_id = request_dict.get("image_code_id")
    if not all ([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数不能为空")
    if not re.match(r"1[3-9]\d{9}",mobile):
        return jsonify(errno=RET.DATAERR,errmsg="手机号输入有误,请重新输入!")
    try:
        redis_image_code = redis_store.get("image_code:%s"%image_code_id)
        # print (redis_image_code)
        if not redis_image_code:
            return jsonify(errno=RET.NODATA,errmsg="验证码已过期,请重新输入!")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="提取验证码错误!")
    try:
        if image_code.lower() != redis_image_code.lower():
            redis_store.delete(image_code_id)
            return jsonify(errno=RET.DATAERR,errmsg="验证码输入有误！")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="删除图片验证码失败！")
    if image_code.lower() == redis_image_code.lower():
        # return jsonify(errno=RET.OK, errmsg="验证码输入正确！")
        sms_num = "%06d"%random.randint(0,999999)
        # ccp = CCP()
        # result = ccp.send_template_sms(mobile, [sms_num, constants.SMS_CODE_REDIS_EXPIRES/60], 1)
        result = 0
    try:
        if result  == 0:
            redis_store.set("sms_code:%s"%mobile,sms_num,constants.SMS_CODE_REDIS_EXPIRES)
            return jsonify(errno=RET.OK,errmsg="验证码已发送")
        elif result == -1:
            return jsonify(errno=RET.THIRDERR,errmsg="发送短信验证码失败!")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据库插入失败！")

    # return ('hello sms_code')

#图片验证码
@passport_bule.route('/image_code')
def get_code():
    """
        1.获取参数
        2.校验参数,cur_id
        3.判断是否有上个pre_id,如果有则删除redis中上次图片验证码
        4.生成图片验证码,并存储到redis中
        5.返回图片验证码
        :return:
    """
    # redis_store.set()
    cur_code_id = request.args.get("cur_id")
    per_code_id = request.args.get("pre_id")

    if not cur_code_id:
        return "图片编码不能为空"
    try:
        if per_code_id:
            redis_store.delete("image_code:%s"%per_code_id)
    except Exception as e:
        current_app.logger.error(e)

    try:
        image_code_id, text, image_data = captcha.captcha.generate_captcha()
        redis_store.set("image_code:%s"%cur_code_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return ("存储图片失败")

    response = make_response(image_data)
    response.headers['Content-Type'] = "image/jpg"

    return response

     # print (text)

