from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app import db
from models.proveedor import Proveedor

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.route('/')
@login_required
def index():
    suppliers = Proveedor.query.all()
    return render_template('proveedores/index.html', suppliers=suppliers)

@proveedores_bp.route('/add', methods=['POST'])
@login_required
def add():
    name = request.form.get('name')
    cuit = request.form.get('cuit')
    contact_name = request.form.get('contact_person') or request.form.get('contact_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    
    if not name:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
            return jsonify({'success': False, 'error': 'El nombre es obligatorio'}), 400
        flash('El nombre de la empresa es obligatorio', 'danger')
        return redirect(url_for('proveedores.index'))
        
    new_supplier = Proveedor(
        name=name,
        cuit=cuit,
        contact_name=contact_name,
        email=email,
        phone=phone,
        address=address
    )
    
    db.session.add(new_supplier)
    db.session.commit()
    
    # Si es una petición AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.accept_mimetypes.accept_json:
        return jsonify({'success': True, 'id': new_supplier.id, 'name': new_supplier.name})
    
    flash('Proveedor agregado exitosamente', 'success')
    return redirect(url_for('proveedores.index'))

@proveedores_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    supplier = Proveedor.query.get_or_404(id)
    supplier.name = request.form.get('name')
    supplier.cuit = request.form.get('cuit')
    supplier.contact_name = request.form.get('contact_name')
    supplier.email = request.form.get('email')
    supplier.phone = request.form.get('phone')
    supplier.address = request.form.get('address')
    
    db.session.commit()
    flash('Proveedor actualizado', 'success')
    return redirect(url_for('proveedores.index'))

@proveedores_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    supplier = Proveedor.query.get_or_404(id)
    
    # Verificar si tiene productos asociados
    if supplier.productos.count() > 0:
        flash('No se puede eliminar: tiene productos asociados', 'danger')
        return redirect(url_for('proveedores.index'))
        
    db.session.delete(supplier)
    db.session.commit()
    flash('Proveedor eliminado', 'success')
    return redirect(url_for('proveedores.index'))
