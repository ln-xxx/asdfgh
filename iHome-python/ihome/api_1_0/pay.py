


from . import api
from ihome.utils.commons import login_required
from ihome.models import Order
from flask import g, current_app, jsonify, request
from ihome.utils.response_code import RET
from alipay import AliPay
from ihome import constants, db
import os
@api.route("/orders/<int:order_id>/payment", methods=["POST"])
@login_required
def order_pay(order_id):
    """发起支付宝支付
    大致流程：
    获取用户的编号
    判断该订单的状态
    配置支付宝接口
    生成支付宝链接
    返回结果
    """
    user_id = g.user_id
    # 判断订单状态
    try:
        order = Order.query.filter(Order.id == order_id, Order.user_id ==
                                   user_id, Order.status == "WAIT_PAYMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库异常")
    if order is None:
        return jsonify(errno=RET.NODATA, errmsg="订单数据有误")
    # 创建支付宝sdk的工具对象
    app_private_key_string = open(os.path.join(os.path.dirname(__file__), 'keys/app_private_key.pem')).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), 'keys/app_public_key.pem')).read()
    alipay_client = AliPay(
        appid="2016110300790404",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2",
        debug=True
    )
    # 手机网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? +order_string
    order_string = alipay_client.api_alipay_trade_wap_pay(
        out_trade_no=order.id,  # 订单编号
        total_amount=str(order.amount / 100.0),  # 总金额
        subject=u"爱家租房 %s" % order.id,  # 订单标题
        return_url="http://127.0.0.1:5000/payComplete.html",  # 返回的连接地址
        notify_url=None  # 可选, 不填则使用默认notify url
    )
    # 构建让用户跳转的支付连接地址
    pay_url = constants.ALIPAY_URL_PREFIX + order_string
    return jsonify(errno=RET.OK, errmsg="OK", data={"pay_url": pay_url})



@api.route("/order/payment", methods=["PUT"])
def save_order_payment_result():
    """保存订单支付结果"""
    alipay_dict = request.form.to_dict()
    print(alipay_dict)
    # 对支付宝的数据进行分离 提取出支付宝的签名参数sign 和剩下的其他数据
    # 从字典alipay_dict中取出sign的同时将sign从alipay_dict中删除
    alipay_sign = alipay_dict.pop("sign")
    print('-'*100)
    print(alipay_sign)
    # 创建支付宝sdk的工具对象
    # 创建支付宝sdk的工具对象
    app_private_key_string = open(os.path.join(os.path.dirname(__file__), 'keys/app_private_key.pem')).read()
    alipay_public_key_string = open(os.path.join(os.path.dirname(__file__), 'keys/app_public_key.pem')).read()
    # app_private_key_string = open(os.path.join(os.path.dirname(__file__), 'keys/app_private_key.pem')).read()
    # alipay_public_key_string = open(os.getcwd()+"\ihome/api_1_0\keys/pu.pem").read()
    # app_private_key_string = open(os.getcwd() + "\ihome/api_1_0\keys\kapp_private_key.pem").read()
    # # app_private_key_string = open(".\keys\keysapp_private_key").read()
    # alipay_public_key_string = open(os.getcwd() + "\ihome/api_1_0\keys/app_public_key.pem").read()
    alipay_client = AliPay(
        appid="2016110300790404",
        app_notify_url=None,
        app_private_key_string=app_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        # app_private_key_string=os.path.join(os.path.dirname(__file__), "keys/app_private_key.pem"),
        # alipay_public_key_string=os.path.join(os.path.dirname(__file__), "keys/alipay_public_key.pem"),
        sign_type="RSA2",
        debug=True
    )
    # 借助工具验证参数的合法性
    # 如果确定参数是支付宝的，返回True，否则返回false
    # alipay_dict支付宝回传的参数除了sign外的内容
    # alipay_client.verify(alipay_dict, alipay_sign)：将回传参数通过支付宝加密后和之前
    # 支付宝传递的签名信息alipay_sign进行比较
    # 如果True:成功，否则失败
    result = alipay_client.verify(alipay_dict, alipay_sign)
    print('*'*100)
    print(result)
    # if result and alipay_dict["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
    #     print("trade succeed")
    if result:
        # 修改数据库的订单状态信息
        order_id = alipay_dict.get("out_trade_no")
        trade_no = alipay_dict.get("trade_no")  # 支付宝的交易号
        try:
            Order.query.filter_by(id=order_id).update({"status": "COMPLETE","trade_no": trade_no})
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    return jsonify(errno=RET.OK, errmsg="OK")






