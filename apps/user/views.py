import hashlib

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g
# 导入werkzeug内置的密码加密模块
from werkzeug.security import generate_password_hash, check_password_hash
# 创建蓝图对象
from ext import db
from user.models import User
from apps.user.smssend import SmsSendAPIDemo

# 创建蓝图对象,url_prefix指定路由前缀
user_bp = Blueprint('user',__name__,url_prefix='/user')


# 使用蓝图绑定路由
# @user_bp.route('/')
# def hello_world():
#     return 'Hello World!'


@user_bp.route('/register',methods=['GET','POST'])
def register():
    """注册"""
    # post请求
    if request.method == 'POST':
        # 接收表单参数
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        email = request.form.get('email')
        # 判断两次密码是否一致
        if password == repassword:
            # 注册用户并给属性赋值
            user = User()
            user.username = username
            # 使用自带的函数实现加密：generate_password_hash
            user.password = generate_password_hash(password)
            print(password)
            user.phone = phone
            user.email = email
            # 添加并提交
            db.session.add(user)
            db.session.commit()
            # 重定向到首页
            return redirect(url_for('user.index'))
    return render_template('user/register.html')


@user_bp.route('check_username',methods=['GET','POST'])
def check_username():
    """校验用户名是否重复注册"""
    # 接收参数
    username = request.args.get('username')
    # 根据用户名查询
    user = User.query.filter_by(username=username).first()
    # 用户已注册，渲染错误信息
    if user:
        return jsonify(code=400,msg='此用户名已注册')
    else:
        return jsonify(code=200,msg='此用户名可用')


@user_bp.route('/checkphone',methods=['GET','POST'])
def check_phone():
    """验证手机号是否重复注册"""
    # 1.接收参数
    phone = request.args.get('phone')
    # 2.查询用户手机号，得到用户列表
    user = User.query.filter(User.phone == phone).all()
    print(user)
    # code: 400 不能用    200 可以用
    if len(user) > 0: # 如果user列表长度大于0,表示用户已注册
        # 返回json数据
        return jsonify(code=400, msg='此号码已被注册')
    else:
        return jsonify(code=200, msg='此号码可用')


@user_bp.route('/login',methods=['GET','POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        f = request.args.get('f')
        if f == '1':
            username = request.form.get('username')
            password = request.form.get('password')
            # 查询用户列表
            users = User.query.filter(User.username==username).all()

            for user in users:
                # 校验密码
                # 如果flag=True表示匹配，否则密码不匹配
                flag = check_password_hash(user.password,password)
                if flag:
                    # return '用户登录成功'
                    # 方式一：通过cookie实现会话保存
                    # response = redirect(url_for('user.index'))
                    # # 设置cookie,max_age设置cookie过期时间，单位为秒
                    # response.set_cookie('uid', str(user.id),max_age=3600)
                    # return response
                    # 方式二：使用session实现状态保持
                    session['uid'] = user.id
                    return redirect(url_for('user.index'))

            else:
                return render_template('user/login.html', msg='用户名或者密码有误')

        elif f == '2':  # 手机号码与验证码
            # 接收表单参数
            phone = request.form.get('phone')
            code = request.form.get('code')
            valid_code = session.get(phone)
            print('valid_code:' + str(valid_code))
            # 先验证验证码
            if code == valid_code:
                # 查询用户输入的手机号是否和数据库相同
                user = User.query.filter(User.phone==phone).first()
                print(user)
                # 如果user存在，则写入到session中
                if user:
                    session['uid'] = user.id
                    # 重定向到首页
                    return redirect(url_for('user.index'))
                else: # 不存在则渲染错误信息
                    return render_template('user/login.html', msg='此号码未注册')
            else: # 验证码错误
                return render_template('user/login.html',msg='验证码有误！')
    # get请求
    return render_template('user/login.html')




@user_bp.route('/')
def index():
    """首页"""
    # 从请求头获取cookie信息
    # uid = request.cookies.get('uid',None)
    # 使用session保存用户状态
    uid = session.get('uid')
    # 如果uid存在，表示用户登录成功
    if uid:
        user = User.query.get(uid)
        return render_template('user/index.html',user=user)
    else: # 用户未登录
        return render_template('user/index.html')


@user_bp.route('/logout')
def logout():
    """用户退出"""
    response = redirect(url_for('user.index'))
    # 删除浏览器保存的cookie
    # response.delete_cookie('uid')

    # 删除指定值
    # del session['uid']  # 只会删除session中的这个键值对，不会删除session空间和cookie
    session.clear() # 删除session中所有的值，将服务端和客户端session都删除
    return response

@user_bp.route('/sendMsg')
def send_message():
    phone = request.args.get('phone')
    # 补充验证手机号码是否注册，去数据库查询

    SECRET_ID = "dcc535cbfaefa2a24c1e6610035b6586"  # 产品密钥ID，产品标识
    SECRET_KEY = "d28f0ec3bf468baa7a16c16c9474889e"  # 产品私有密钥，服务端生成签名信息使用，请严格保管，避免泄露
    BUSINESS_ID = "748c53c3a363412fa963ed3c1b795c65"  # 业务ID，易盾根据产品业务特点分配
    api = SmsSendAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)
    params = {
        "mobile": phone,
        "templateId": "10084",
        "paramType": "json",
        "params": "json格式字符串"
    }
    ret = api.send(params)
    print(ret)
    session[phone] = '189075'
    return jsonify(code=200, msg='短信发送成功！')
