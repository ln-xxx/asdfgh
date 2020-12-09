#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

from flask import current_app, jsonify, make_response, request

# from ihome.tasks.tasks_sms import send_sms
from . import api
from ihome.utils.captcha.captcha import captcha
from ihome import redis_store, constants, db
from ihome.utils.response_code import RET
from ihome.models import User

# from allTasks.tasks.sms.tasks import send_sms
from ..utils.sms_code import get_code


@api.route('/image_codes/<image_code_id>')
def get_image_code(image_code_id):
    """
    获取验证码图片
    :param image_code_id: 图片验证码编号
    :return: 如果出现异常，返回异常信息，否则，返回验证码图片
    """
    # 生成验证码图片
    # 名字，真是文本，图片数据
    name, text, image_code = captcha.generate_captcha()

    # 将编号以及验证码的真实值保存到redis（选择字符串）中，并设置有效期（自定义有效期为180秒，设置成了常量，在constants中）
    # redis_store.set('iamge_code_%s' % image_code_id, text)
    # redis_store.expire('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES)
    # 将以上合并写
    try:
        redis_store.setex('image_code_%s' % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        # 记录日志
        current_app.logger.error(e)
        # 出现异常，返回json格式的提示
        # return jsonify(errno=RET.DBERR, errmsg="save image code failed")
        return jsonify(errno=RET.DBERR, errmsg="保存图片验证码失败")

    # 没有异常 返回验证码图片，并指定一下Content-Type(默认为test/html)类型为image,不改不认识图片
    resp = make_response(image_code)
    resp.headers['Content-Type'] = 'image/jpg'
    return resp

from ihome.utils.sms_code import get_sms_code
@api.route('sms_codes/<mm>',methods=['GET'])
def smsz_conde(mm):
    bb=get_code(6, False)
    print(bb)
    get_sms_code(mm,bb )
    try:
        redis_store.setex("sms_code_%s" % mm, constants.SMS_CODE_REDIS_EXPIRES, bb)
        redis_store.setex("send_sms_code_%s" % mm, constants.SEND_SMS_CODE_INTERVAL, 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存短信验证码异常")
    return jsonify(errno=RET.OK, errmsg="短信发送成功！！！")




