# app/routes/admin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.admin import Admin
from app.controllers.admin_controller import login_admin, logout_admin

bp = Blueprint('admin', __name__)

@bp.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if login_admin(username, password):
            session['admin'] = True
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('admin_login.html')

@bp.route('/admin/logout', methods=['POST'])
def logout():
    logout_admin()
    session.pop('admin', None)
    return redirect(url_for('admin.login'))

@bp.route('/admin/dashboard', methods=['GET'])
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin.login'))
    return render_template('dashboard.html')