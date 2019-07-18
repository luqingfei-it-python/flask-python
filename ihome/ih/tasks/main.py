from celery import Celery
from ih.tasks import config

# 创建Celery对象
celery_app = Celery("ih")

# 引入配置信息
celery_app.config_from_object(config)

# 自动搜寻异步任务
celery_app.autodiscover_tasks(["ih.tasks.sms"])

# 启动方式
# celery -A ih.tasks.main worker -l info -P eventlet
