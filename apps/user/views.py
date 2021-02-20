import os

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from apps.article.models import Article_type, Article
from apps.user.models import User, Photo
from apps.user.smssend import SmsSendAPIDemo
from apps.utils.qiniu import upload_qiniu, delete_qiniu
from exts import db
from settings import Config

user_bp1 = Blueprint('user', __name__, url_prefix='/user')

# 用于存储登录后的用户路由列表
required_login_list = ['/user/center',
                       '/user/change',
                       '/article/publish',
                       '/user/upload_photo',
                       '/user/delete_qiniu'
                        ]


# @user_bp1.before_app_first_request
# def first_request():
#     """第一次请求调用"""
#     print('before_app_first_request')


# ****重点*****
@user_bp1.before_app_request
def before_request1():
    """每次请求调用"""
    print('before_request1before_request1', request.path)
    if request.path in required_login_list:
        id = session.get('uid')
        if not id:
            return render_template('user/login.html')
        else:
            user = User.query.get(id)
            # g对象，本次请求的对象
            g.user = user


# @user_bp1.after_app_request
# def after_request_test(response):
#     response.set_cookie('a', 'bbbb', max_age=19)
#     print('after_request_test')
#     return response


# @user_bp1.teardown_app_request
# def teardown_request_test(response):
#     print('teardown_request_test')
#     return response


# 自定义过滤器
@user_bp1.app_template_filter('cdecode')
def content_decode(content):
    content = content.decode('utf-8')
    return content[:200]



@user_bp1.route('/')
def index():
    """首页"""
    # 1。cookie获取方式
    # uid = request.cookies.get('uid', None)
    # 2。session的获取,session底层默认获取
    # 2。session的方式：
    uid = session.get('uid')
    # 获取文章列表   7 6 5  |  4 3 2 | 1
    # 接收页码数
    page = int(request.args.get('page', 1))
    pagination = Article.query.order_by(-Article.pdatetime).paginate(page=page, per_page=3)
    print(pagination.items)  # [<Article 4>, <Article 3>, <Article 2>]
    print(pagination.page)  # 当前的页码数
    print(pagination.prev_num)  # 当前页的前一个页码数
    print(pagination.next_num)  # 当前页的后一页的页码数
    print(pagination.has_next)  # True
    print(pagination.has_prev)  # True
    print(pagination.pages)  # 总共有几页
    print(pagination.total)  # 总的记录条数
    # 获取分类列表
    types = Article_type.query.all()
    # 判断用户是否登录
    if uid:
        user = User.query.get(uid)
        return render_template('user/index.html', user=user, types=types, pagination=pagination)
    else:
        return render_template('user/index.html', types=types, pagination=pagination)


@user_bp1.route('/checkphone', methods=['GET', 'POST'])
def check_phone():
    """手机号码验证"""
    phone = request.args.get('phone')
    user = User.query.filter(User.phone == phone).all()
    print(user)
    # code: 400 不能用    200 可以用
    if len(user) > 0:
        return jsonify(code=400, msg='此号码已被注册')
    else:
        return jsonify(code=200, msg='此号码可用')


@user_bp1.route('/check_username',methods=['GET','POST'])
def check_username():
    """校验用户名是否重复注册"""
    # 接收参数
    username = request.args.get('username')
    # 根据用户名查询
    user = User.query.filter_by(username=username).first()
    # 用户已注册，渲染错误信息
    if user:
        return jsonify(code=400, msg='此用户名已注册')
    else:
        return jsonify(code=200, msg='此用户名可用')

@user_bp1.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        email = request.form.get('email')
        if password == repassword:
            # 注册用户
            user = User()
            user.username = username
            # 使用自带的函数实现加密：generate_password_hash
            user.password = generate_password_hash(password)
            # print(password)
            user.phone = phone
            user.email = email
            # 添加并提交
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('user.index'))
    return render_template('user/register.html')







@user_bp1.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    # post请求
    if request.method == 'POST':
        f = request.args.get('f')
        if f == '1':  # 用户名或者密码
            username = request.form.get('username')
            password = request.form.get('password')
            # 过滤查询条件：用户输入的用户和数据库用户名相同
            users = User.query.filter(User.username == username).all()
            for user in users: # 遍历用户列表
                # 如果flag=True表示匹配，否则密码不匹配
                flag = check_password_hash(user.password, password)
                if flag:
                    # 1。cookie实现机制
                    # response = redirect(url_for('user.index'))
                    # response.set_cookie('uid', str(user.id), max_age=1800)
                    # return response
                    # 2.将用户的信息存储在session中，以字典的形式存储
                    session['uid'] = user.id
                    return redirect(url_for('user.index'))
            else:
                return render_template('user/login.html', msg='用户名或者密码有误')
        elif f == '2':  # 手机号码与验证码
            print('----->22222')
            phone = request.form.get('phone')
            code = request.form.get('code')
            # 获取当前登录用户的手机号验证码
            valid_code = session.get(phone)
            # 将验证码转成字符串
            print('valid_code:' + str(valid_code))
            if code == valid_code: # 判断验证码
                # 查询用户输入的手机号是否和数据库相同
                user = User.query.filter(User.phone == phone).first()
                print(user)
                if user: # user存在,登录成功，将用户的信息写入到session中
                    session['uid'] = user.id
                    # 重定向到首页
                    return redirect(url_for('user.index'))
                else: # 不存在，渲染提示信息
                    return render_template('user/login.html', msg='此号码未注册')
            else:
                return render_template('user/login.html', msg='验证码有误！')
    # get请求
    return render_template('user/login.html')


@user_bp1.route('/sendMsg')
def send_message():
    """发送短信息"""
    phone = request.args.get('phone')
    # 补充验证手机号码是否注册，去数据库查询

    SECRET_ID = "dcc535cbfaefa2a24c1e6610035b6586"  # 产品密钥ID，产品标识
    SECRET_KEY = "d28f0ec3bf468baa7a16c16c9474889e"  # 产品私有密钥，服务端生成签名信息使用，请严格保管，避免泄露
    BUSINESS_ID = "748c53c3a363412fa963ed3c1b795c65"  # 业务ID，易盾根据产品业务特点分配
    api = SmsSendAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)
    params = {
        "mobile": phone,
        "templateId": "11732",
        "paramType": "json",
        "params": "json格式字符串"
    }
    ret = api.send(params)
    print(ret)
    # session[phone] = '189075'
    # return jsonify(code=200, msg='短信发送成功！')

    if ret is not None:
        if ret["code"] == 200:
            taskId = ret["result"]["taskId"]
            print("taskId = %s" % taskId)
            session[phone] = '189075'
            return jsonify(code=200, msg='短信发送成功！')
        else:
            print("ERROR: ret.code=%s,msg=%s" % (ret['code'], ret['msg']))
            return jsonify(code=400, msg='短信发送失败！')



@user_bp1.route('/logout')
def logout():
    """用户退出"""
    # 1. cookie的方式
    # response = redirect(url_for('user.index'))
    # 通过response对象的delete_cookie(key),key就是要删除的cookie的key
    # response.delete_cookie('uid')
    # 2.session的方式
    # del session['uid']
    session.clear()
    return redirect(url_for('user.index'))



@user_bp1.route('/center')
def user_center():
    """用户中心"""
    types = Article_type.query.all()
    # 查询当前登录用户上传的相片
    photos = Photo.query.filter(Photo.user_id == g.user.id).all()
    return render_template('user/center.html', user=g.user, types=types, photos=photos)


# 图片的扩展名
ALLOWED_EXTENSIONS = ['jpg', 'png', 'gif', 'bmp']


# 用户信息修改
@user_bp1.route('/change', methods=['GET', 'POST'])
def user_change():
    if request.method == 'POST':
        username = request.form.get('username')
        phone = request.form.get('phone')
        email = request.form.get('email')
        # 只要有文件（图片），获取方式必须使用request.files.get(name)
        icon = request.files.get('icon')
        # print('======>', icon)  # FileStorage
        # 属性： filename 用户获取文件的名字
        # 方法:  save(保存路径)
        icon_name = icon.filename  # 1440w.jpg
        suffix = icon_name.rsplit('.')[-1]
        if suffix in ALLOWED_EXTENSIONS:
            icon_name = secure_filename(icon_name)  # 保证文件名是符合python的命名规则
            file_path = os.path.join(Config.UPLOAD_ICON_DIR, icon_name)
            icon.save(file_path)
            # 保存成功
            user = g.user #
            user.username = username
            user.phone = phone
            user.email = email
            path = 'upload/icon'
            user.icon = os.path.join(path, icon_name)
            db.session.commit()
            return redirect(url_for('user.user_center'))
        else:
            return render_template('user/center.html', user=g.user, msg='必须是扩展名是：jpg,png,gif,bmp格式')

    return render_template('user/center.html', user=g.user)



@user_bp1.route('/article', methods=['GET', 'POST'])
def publish_article():
    """发表文章"""
    if request.method == 'POST':
        title = request.form.get('title')
        type = request.form.get('type')
        content = request.form.get('content')
        print(title, type, content)

        return render_template('article/test.html', content=content)
    return '发表失败！'


@user_bp1.route('/upload_photo', methods=['GET', 'POST'])
def upload_photo():
    """上传照片"""
    # 获取上传的内容
    photo = request.files.get('photo')  # 返回的是一个文件存储对象(FileStorage)
    # photo.filename,photo.save(path)
    # 调用qiniu提供方法上传图片
    ret, info = upload_qiniu(photo)
    if info.status_code == 200: # 状态返回的状态码
        photo = Photo() # 创建photo对象
        photo.photo_name = ret['key'] # key表示上传文件的名字
        photo.user_id = g.user.id # 当前登录的用户
        db.session.add(photo) # 添加并提交到数据库
        db.session.commit()
        return '上传成功！'
    else:
        return '上传失败！'


@user_bp1.route('/myphoto')
def myphoto():
    """展示我的相册"""
    # 接收分页参数,page表示所在页，默认为第1页
    page = int(request.args.get('page', 1))
    # 分页操作，per_page一页显示3条数据
    photos = Photo.query.paginate(page=page, per_page=3)
    user_id = session.get('uid',None) # 从session中获取登录用户的uid
    user = None
    if user_id: # 用户已登录，根据用户id查询数据库
        user = User.query.get(user_id)
    # 渲染模板
    return render_template('user/myphoto.html', photos=photos, user=user)


@user_bp1.route('/photo_del')
def photo_del():
    """删除相册"""
    # 1.接收要删除的pid(表示相册的id)
    pid = request.args.get('pid')
    # 2.查询pid是否有效
    photo = Photo.query.get(pid)
    # 获取相片名称
    filename = photo.photo_name
    # 调用七牛云封装的删除的文件函数
    info = delete_qiniu(filename) # 将要删除的文件名传递给函数
    # 判断返回的状态码
    if info.status_code == 200:
        # 再删除数据库中的内容，并提交
        db.session.delete(photo)
        db.session.commit()
        # 重定向到用户中心
        return redirect(url_for('user.user_center'))
    else:
        return render_template('500.html',msg='删除相册图片失败！')




@user_bp1.route('/error')
def test_error():
    # print(request.headers)
    # print(request.headers.get('Accept-Encoding'))
    referer = request.headers.get('Referer', None)
    return render_template('500.html', err_msg='有误', referer=referer)
