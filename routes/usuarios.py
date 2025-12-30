from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models.usuario import Usuario
from functools import wraps

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@usuarios_bp.route('/')
@login_required
@admin_required
def index():
    users = Usuario.query.all()
    return render_template('usuarios/index.html', users=users)

@usuarios_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        if Usuario.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return redirect(url_for('usuarios.create'))
            
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado.', 'danger')
            return redirect(url_for('usuarios.create'))
            
        user = Usuario(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Usuario creado correctamente.', 'success')
        return redirect(url_for('usuarios.index'))
        
    return render_template('usuarios/create.html')

@usuarios_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(id):
    user = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        user.role = request.form.get('role')
        
        password = request.form.get('password')
        if password:
            user.set_password(password)
            
        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('usuarios.index'))
        
    return render_template('usuarios/edit.html', user=user)

@usuarios_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete(id):
    if current_user.id == id:
        flash('No puedes eliminar tu propio usuario.', 'danger')
        return redirect(url_for('usuarios.index'))
        
    user = Usuario.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    
    flash('Usuario eliminado correctamente.', 'success')
    return redirect(url_for('usuarios.index'))
