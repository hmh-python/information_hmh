#encoding:utf-8
import datetime
import random
from info import curren_app,db,models
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app = curren_app("Develo")

manager =  Manager(app)

Migrate(app,db)

manager.add_command("db",MigrateCommand)

@manager.option('-n','--name',dest='username')
@manager.option('-p','--password',dest='password')
def create_superuser(username,password):

    user = models.User()
    user.nick_name = username
    user.mobile = username
    user.password = password
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        curren_app.logger.error(e)
        return "创建失败!"
#
# @manager.option('-t','--test',dest='usertest')
# def create_testuser(usertest):
#
#     user_list = [ ]
#
#     for i in range(3002,4001):
#         user = models.User()
#         user.nick_name = '老王%d'%i
#         user.password = '111111'
#         user.mobile = '1380000%04d'%i
#         user.last_login = datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0, 3600 * 24 * 31))
#         user_list.append(user)
#
#     try:
#         db.session.add(user_list)
#         db.session.commit()
#     except Exception as e:
#         curren_app.logger.error(e)
#         db.session.rollback()
#         return '创建失败!'
#     return '创建成功!'

if __name__ == '__main__':
    manager.run()