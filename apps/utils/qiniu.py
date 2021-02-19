import random

from qiniu import Auth, put_data


def upload_qiniu(filestorage):
    """封装七牛云工具"""
    access_key = 'bZlGPCXm3Bt6SPqQeY3G9-Te4PiCHOUlOVuEQWM1'
    secret_key = '9ttO0AXliBgiUQvMHPsGHPaOXpiqazp6uvDv11nW'
    q = Auth(access_key,secret_key)
    # 七牛云上创建的存储空间名
    bucket_name = 'lisa530'
    # 获取上传后保存的文件名
    filename = filestorage.filename
    # 随机生成随机数
    ran = random.randint(1,1000)
    # 将上传的文件名进行切片,得到文件后缀名
    suffix = filename.rsplit('.')[-1]
    # 拼接完整的文件名（xxx3451_982.jpg )
    key = filename.rsplit('.')[0] + '_' + str(ran) + '.' + suffix
    # 生成上传token 调用q.upload_token,接收三个参数：
    # 要上传的文字名，过期时间
    token = q.upload_token(bucket_name,key,3600)
    ret,info = put_data(token,key,filestorage.read())
    # ret:返回文件名,info返回上传的状态码
    return ret,info
