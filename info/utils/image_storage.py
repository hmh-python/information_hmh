# -*- coding: utf-8 -*-
# flake8: noqa
from qiniu import Auth, put_file, etag,put_data
import qiniu.config
#需要填写你的 Access Key 和 Secret Key

access_key = 'B-VnP3t4scTirkum3lYmgWbE_ZkBnZS9QwhorxrX'
secret_key = 'ka_PLwjPOt8xl_DbbfktmS9zRnFB7a5VkkhGvYuF'

def image_stor(image_data):

    #构建鉴权对象
    q = Auth(access_key, secret_key)
    #要上传的空间
    bucket_name = 'information-hmh'
    #上传到七牛后保存的文件名
    key = None
    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)
    #要上传文件的本地路径
    # localfile = './sync/bbb.jpg'

    # ret, info = put_file(token, key, image_data)
    ret, info = put_data(token, key, image_data)
    # print(info)
    # assert ret['key'] == key
    # assert ret['hash'] == etag(image_data)
    if info.status_code == 200:
        return  ret.get('key')
    else:
        return ""

if __name__ == '__main__':
    with open ('./21.jpg','rb') as f:
        image =  image_stor(f.read())
        print(image)