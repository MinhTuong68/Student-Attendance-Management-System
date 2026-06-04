from flask import Flask
import os
from flask_login import LoginManager

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = 'phungminhtuong16dth2'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Khởi tạo DB
    from app.models import db
    db.init_app(app)

    # Khởi tạo Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from app.models.admin import Admin

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    # Đăng ký blueprints
    from app.blueprints.public import public_bp
    from app.blueprints.auth   import auth_bp
    from app.blueprints.admin  import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp,  url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        from app.models.admin import Admin
        from app.models.student import Student
        from app.models.attendance import Attendance

        db.create_all()
        _seed_admin()

    return app

def _seed_admin():
    from app.models.admin import Admin
    from app.models import db
    if not Admin.query.first():
        a = Admin(username='admin')
        a.set_password('admin123')
        db.session.add(a)
        db.session.commit()
        print('✅ Tạo admin mặc định: admin / admin123')
    

