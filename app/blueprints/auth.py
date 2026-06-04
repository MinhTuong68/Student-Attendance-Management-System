from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, current_user
from app.models.admin import Admin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin_user = Admin.query.filter_by(username=username).first()

        if admin_user and admin_user.check_password(password):
            login_user(admin_user)  # Tạo session đăng nhập bảo mật
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không chính xác!', 'error')
            
    return render_template('auth/login.html')