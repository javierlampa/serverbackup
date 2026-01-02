from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models import Mantenimiento, Producto, Categoria
from datetime import datetime

mantenimientos_bp = Blueprint('mantenimientos', __name__)

@mantenimientos_bp.route('/')
@login_required
def index():
    mantenimientos = Mantenimiento.query.order_by(Mantenimiento.fecha_inicio.desc()).all()
    
    # Filtrar productos para que solo aparezcan PCs y Notebooks
    productos = Producto.query.join(Categoria).filter(
        (Categoria.name.ilike('%PC%')) | (Categoria.name.ilike('%Notebook%'))
    ).order_by(Producto.name).all()
    
    return render_template('mantenimientos/index.html', 
                           mantenimientos=mantenimientos,
                           productos=productos)

@mantenimientos_bp.route('/add', methods=['POST'])
@login_required
def add():
    producto_id = request.form.get('producto_id', type=int)
    tipo = request.form.get('tipo')
    descripcion = request.form.get('descripcion')
    costo = request.form.get('costo', 0.0, type=float)
    tecnico = request.form.get('tecnico')
    
    if not producto_id or not tipo or not descripcion:
        flash('Por favor complete los campos obligatorios.', 'danger')
        return redirect(url_for('mantenimientos.index'))
    
    producto = Producto.query.get(producto_id)
    if not producto or not (('PC' in producto.categoria.name.upper()) or ('NOTEBOOK' in producto.categoria.name.upper())):
        flash('Solo se pueden registrar mantenimientos para PCs y Notebooks.', 'danger')
        return redirect(url_for('mantenimientos.index'))
    
    nuevo_mantenimiento = Mantenimiento(
        producto_id=producto_id,
        tipo=tipo,
        descripcion=descripcion,
        costo=costo,
        tecnico=tecnico,
        estado='en_proceso'
    )
    
    # Opcional: Cambiar estado del producto a 'mantenimiento'
    producto = Producto.query.get(producto_id)
    if producto:
        producto.status = 'mantenimiento'
    
    db.session.add(nuevo_mantenimiento)
    db.session.commit()
    
    flash('Mantenimiento registrado correctamente.', 'success')
    return redirect(url_for('mantenimientos.index'))

@mantenimientos_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    mantenimiento = Mantenimiento.query.get_or_404(id)
    
    mantenimiento.tipo = request.form.get('tipo')
    mantenimiento.descripcion = request.form.get('descripcion')
    mantenimiento.costo = request.form.get('costo', 0.0, type=float)
    mantenimiento.tecnico = request.form.get('tecnico')
    mantenimiento.estado = request.form.get('estado')
    
    if mantenimiento.estado == 'completado' and not mantenimiento.fecha_fin:
        mantenimiento.fecha_fin = datetime.utcnow()
        # Opcional: Devolver producto a 'disponible'
        if mantenimiento.producto:
            mantenimiento.producto.status = 'disponible'
            
    db.session.commit()
    flash('Mantenimiento actualizado correctamente.', 'success')
    return redirect(url_for('mantenimientos.index'))

@mantenimientos_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    mantenimiento = Mantenimiento.query.get_or_404(id)
    db.session.delete(mantenimiento)
    db.session.commit()
    flash('Registro de mantenimiento eliminado.', 'success')
    return redirect(url_for('mantenimientos.index'))
