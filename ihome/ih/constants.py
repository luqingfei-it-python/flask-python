
# 图片验证码保存时间    单位：秒
IMAGE_CODE_EXPIRE_TIME = 180

# 短信验证码保存时间    单位：秒
SMS_CODE_EXPIRE_TIME = 300

# 发送短信验证码的时间间隔 单位：秒
SEND_SMS_CODE_INTERVAL = 60

# 尝试最大登陆错误次数
LOGIN_ERROR_MAX_TIMES = 5

# 被禁止登陆的时间  单位：秒
LOGIN_ERROR_FORBID_TIME = 600

# 七牛保存图片的域名
QINIU_IMAGE_IP_NAME = "http://po8i95b7y.bkt.clouddn.com/"

# 保存在redis中的城区信息有效时间  单位：秒
AREA_INFO_REMACH_EXPIRES = 7200

# 房屋详情页展示最大评论数
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30

# 保存在redis的主页房屋图片的时间 单位：秒
HOME_INDEX_IMAGE_REDIS_EXPIRES = 7200

# 保存在redis中的房屋信息的有效时间 单位：秒
HOME_INFO_REDIS_EXPIRES = 7200

# 首页展示最多房屋数量
HOME_PAGE_MAX_COUNTS = 5

# 每页展示的最大数量
SEARCH_HOME_PAGE_MAX_COUNTS = 2

# 保存在redis中的查询缓存时间
REDIS_CACHE_SEARCH_EXPIRES = 7200

# 支付沙箱网关地址
ALIPAY_PREFIX_URL = "https://openapi.alipaydev.com/gateway.do?"