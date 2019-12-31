from flask import (Flask, redirect, url_for)
from flask_principal import (identity_loaded, UserNeed, RoleNeed)
from flask_login import current_user
from flask_uploads import configure_uploads, patch_request_class

from app.models import db, mongo
from app.ext import (bcrypt, login_manager, principal, file_excel, file_zip, file_tem, file_ork)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_name)
    db.init_app(app)
    mongo.init_app(app)
    bcrypt.init_app(app)
    principal.init_app(app)
    login_manager.init_app(app)

    configure_uploads(app, file_excel)
    configure_uploads(app, file_zip)
    configure_uploads(app, file_tem)
    configure_uploads(app, file_ork)
    patch_request_class(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # 设置当前用户身份为login登录对象
        identity.user = current_user

        # 添加UserNeed到identity user对象
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # 每个Role添加到identity user对象，roles是User的多对多关联
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    @app.route('/')
    def index():
        return redirect(url_for('home.index'))

    from app.home.home import home
    from app.api import api

    app.register_blueprint(home)
    app.register_blueprint(api)

    return app
