from flask_script import (Manager, Server)
from flask_migrate import (Migrate, MigrateCommand)

from app import create_app
from app.config import DevConfig
from app.models import (db, User, Role)
from app.models import sample, qc, patient, report, run_info, template

app = create_app(DevConfig)
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('server', Server())
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_contex():
    return dict(app=app, db=db)


# @manager.shell
# def set_up():
#     db.create_all()
#
#     admin_role = Role(name='admin')
#     admin_role.description = 'admin'
#     db.session.add(admin_role)
#
#     default_role = Role(name='default')
#     default_role.description = 'default'
#     db.session.add(default_role)
#
#     # default_role = Role(name='default') #添加权限 联系 ext
#     # default_role.description = 'default'
#     # db.session.add(default_role)
#
#     admin = User(username='admin')
#     admin.set_password("hm714012636")
#     admin.roles.append(admin_role)
#     admin.roles.append(default_role)
#     db.session.add(admin)
#     db.session.commit()
#     # if Role.query.filter(Role.name == 'admin').first():
#     #     pass
#     # else:
#     #     db.session.commit()


if __name__ == '__main__':
    manager.run()
