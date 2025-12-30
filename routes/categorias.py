from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from models.categoria import Categoria

categorias_bp = Blueprint('categorias', __name__, url_prefix='/categorias')

@categorias_bp.route('/')
@login_required
def index():
    categories = Categoria.query.all()
    
    # Sort categories hierarchically
    def get_category_sort_key(category):
        path = [p.name.lower() for p in category.parents_path]
        path.append(category.name.lower())
        return tuple(path)
        
    categories.sort(key=get_category_sort_key)
    
    return render_template('categorias/index.html', categories=categories)

@categorias_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    description = request.form.get('description')
    color = request.form.get('color', '#3b82f6')
    icon = request.form.get('icon', 'fa-box')
    parent_id = request.form.get('parent_id')
    
    if not name:
        flash('El nombre es obligatorio', 'danger')
        return redirect(url_for('categorias.index'))
        
    existing = Categoria.query.filter_by(name=name).first()
    if existing:
        flash('Ya existe una categoría con ese nombre', 'warning')
        return redirect(url_for('categorias.index'))
    
    # Convert parent_id to integer or None
    if parent_id and parent_id.isdigit():
        parent_id = int(parent_id)
    else:
        parent_id = None

    new_category = Categoria(name=name, description=description, color=color, icon=icon, parent_id=parent_id)
    db.session.add(new_category)
    db.session.commit()
    
    flash('Categoría creada exitosamente', 'success')
    return redirect(url_for('categorias.index'))

@categorias_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    category = Categoria.query.get_or_404(id)
    category.name = request.form.get('name')
    category.description = request.form.get('description')
    category.color = request.form.get('color')
    category.icon = request.form.get('icon')
    
    parent_id = request.form.get('parent_id')
    if parent_id and parent_id.isdigit():
        # Prevent self-referencing
        if int(parent_id) != category.id:
            category.parent_id = int(parent_id)
    else:
        category.parent_id = None
    
    db.session.commit()
    flash('Categoría actualizada', 'success')
    return redirect(url_for('categorias.index'))

@categorias_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    category = Categoria.query.get_or_404(id)
    
    # Verificar si tiene productos asociados
    if category.productos.count() > 0:
        flash('No se puede eliminar: tiene productos asociados', 'danger')
        return redirect(url_for('categorias.index'))
        
    # Verificar si tiene subcategorías
    if category.children.count() > 0:
        flash('No se puede eliminar: tiene subcategorías asociadas', 'danger')
        return redirect(url_for('categorias.index'))
        
    db.session.delete(category)
    db.session.commit()
    flash('Categoría eliminada', 'success')
    return redirect(url_for('categorias.index'))
