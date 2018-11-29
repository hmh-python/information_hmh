from info import curren_app,db,models
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand

app = curren_app("Product")

manager =  Manager(app)

Migrate(app,db)

manager.add_command("db",MigrateCommand)


if __name__ == '__main__':
    manager.run()