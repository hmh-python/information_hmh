from flask import make_response,request,current_app

from info import constants
from info import redis_store

from . import passport_bule
from info.utils.captcha import captcha

@passport_bule.route('/sms_code')
def sms_code():
    pass


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

