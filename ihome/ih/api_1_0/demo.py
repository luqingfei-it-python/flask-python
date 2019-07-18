from . import api
from ih import db, models

@api.route('/index')
def index():
    return "index page"