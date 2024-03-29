from ih import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand



# 创建flask的应用对象
app = create_app('develop')

manage = Manager(app)

Migrate(app, db)

manage.add_command('db', MigrateCommand)



if __name__ == '__main__':
    manage.run()