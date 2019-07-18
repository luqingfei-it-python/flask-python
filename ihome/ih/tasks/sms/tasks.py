from ih.tasks.main import celery_app
from ih.libs.yuntongxun.sms import CCP


@celery_app.task
def send_sms(to, datas, temp_id):
    """发送短信的异步任务"""
    cpp = CCP()
    cpp.send_template_sms(to, datas, temp_id)