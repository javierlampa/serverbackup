import functools
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, g
from ..db import get_db
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Acceso denegado. Se requieren permisos de Administrador.", "error")
            return redirect(url_for('dashboard.index')) # Asumimos dashboard.index
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']
        
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
        
        if user and check_password_hash(user['password'], p):
            session['user_id'] = user['id']
            session['username'] = u
            session['role'] = user['role']
            return redirect(url_for('dashboard.index'))
            
        return render_template('login.html', error="Datos incorrectos")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
