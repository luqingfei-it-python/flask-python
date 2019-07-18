from qiniu import Auth, put_data, etag
import qiniu.config

# 需要填写你的 Access Key 和 Secret Key
access_key = '59Xmxjx2Dhqx0DDdHRw5l3CCks3NypXtKWU91hI3'
secret_key = 'JPkwCqb6aopEMnu5qsQJZXQ0ga_EOkLdUfArbWtR'

def storage(file_data):
    #构建鉴权对象
    q = Auth(access_key, secret_key)

    #要上传的空间
    bucket_name = 'ihome'

    # #上传后保存的文件名
    # key = 'my-python-logo.png'

    #生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, None, 3600)

    #要上传文件的本地路径
    # localfile = './sync/bbb.jpg'    文件的二进制数据
    ret, info = put_data(token, None, file_data)
    # print(info)
    # print("*"*10)
    # print(ret)
    # 判断图片你是否上传成功
    if info.status_code == 200:
        # 图片上传成功
        return ret.get("key")
    else:
        # 上传失败抛出异常提示
        raise Exception("图片上传失败")



if __name__ == '__main__':
    with open("../static/images/home01.jpg", "rb") as f:
        file_data = f.read()

    storage(file_data)