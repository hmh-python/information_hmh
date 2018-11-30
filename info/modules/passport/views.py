import random
import re
from flask import make_response,request,current_app, jsonify,json
from info import constants
from info import redis_store
from info.libs.yuntongxun.sms import CCP
from info.utils.response_code import RET
from . import passport_bule
from info.utils.captcha import captcha

@passport_bule.route('/sms_code',methods=["GET","POST"])
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
    if image_code.lower() != redis_image_code.lower():
        redis_store.delete(image_code_id)
        return jsonify(errno=RET.DATAERR,errmsg="验证码输入有误！")
    if image_code.lower() == redis_image_code.lower():
        # return jsonify(errno=RET.OK, errmsg="验证码输入正确！")
        sms_num = "06%d"%random.randint(0-999999)
        ccp = CCP()
        ccp.send_template_sms(mobile, [sms_num, constants.SMS_CODE_REDIS_EXPIRES/60], 1)

    return ('hello sms_code')

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

