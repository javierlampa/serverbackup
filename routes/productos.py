from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from app import db
from models.producto import Producto
from models.categoria import Categoria
from models.proveedor import Proveedor
from utils.qr_generator import generate_qr_code
from datetime import datetime
import os

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

@productos_bp.route('/')
@login_required
def index():
    # Get filter parameters
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    supplier_id = request.args.get('supplier_id', type=int)
    search_query = request.args.get('q')
    
    # Base query
    query = Producto.query
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(status=status)
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    if search_query:
        query = query.filter(
            (Producto.name.ilike(f'%{search_query}%')) |
            (Producto.code.ilike(f'%{search_query}%')) |
            (Producto.serial_number.ilike(f'%{search_query}%')) |
            (Producto.brand.ilike(f'%{search_query}%')) |
            (Producto.model.ilike(f'%{search_query}%'))
        )
    
    # Get all products
    products = query.order_by(Producto.name).all()
    
    # Get all categories and suppliers for filters
    categories = Categoria.query.order_by(Categoria.name).all()
    suppliers = Proveedor.query.order_by(Proveedor.name).all()
    
    # Get all products for the "parent" selector (PCs, Notebooks, etc.)
    all_products = Producto.query.order_by(Producto.name).all()
    
    return render_template('productos/index.html', 
                         products=products,
                         categories=categories,
                         suppliers=suppliers,
                         all_products=all_products,
                         selected_category=category_id,
                         selected_status=status,
                         selected_supplier=supplier_id,
                         search_query=search_query)

@productos_bp.route('/add', methods=['POST'])
@login_required
def add():
    code = request.form.get('code')
    name = request.form.get('name')
    description = request.form.get('description')
    brand = request.form.get('brand')
    model = request.form.get('model')
    serial_number = request.form.get('serial_number')
    status = request.form.get('status', 'disponible')
    current_stock = request.form.get('current_stock', 0, type=int)
    min_stock = request.form.get('min_stock', 0, type=int)
    location = request.form.get('location')
    reference_price = request.form.get('reference_price', type=float)
    notes = request.form.get('notes')
    category_id = request.form.get('category_id', type=int)
    supplier_id = request.form.get('supplier_id', type=int)
    ip_address = request.form.get('ip_address')
    parent_id = request.form.get('parent_id', type=int)
    ip_address = request.form.get('ip_address')
    parent_id = request.form.get('parent_id', type=int)
    ip_address = request.form.get('ip_address')
    parent_id = request.form.get('parent_id', type=int)
    
    if not code or not name:
        flash('El código y el nombre son obligatorios', 'danger')
        return redirect(url_for('productos.index'))
    
    # Check if code already exists
    existing = Producto.query.filter_by(code=code).first()
    if existing:
        flash('Ya existe un producto con ese código', 'warning')
        return redirect(url_for('productos.index'))
    
    # Check if serial number already exists (if provided)
    if serial_number:
        existing_serial = Producto.query.filter_by(serial_number=serial_number).first()
        if existing_serial:
            flash('Ya existe un producto con ese número de serie', 'warning')
            return redirect(url_for('productos.index'))
    
    # Create product
    new_product = Producto(
        code=code,
        name=name,
        description=description,
        brand=brand,
        model=model,
        serial_number=serial_number,
        status=status,
        current_stock=current_stock,
        min_stock=min_stock,
        location=location,
        reference_price=reference_price,
        notes=notes,
        category_id=category_id if category_id else None,
        supplier_id=supplier_id if supplier_id else None,
        ip_address=ip_address,
        parent_id=parent_id if parent_id else None
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    # Generate QR code
    try:
        qr_path = generate_qr_code(new_product.id, new_product.code)
        new_product.qr_code_path = qr_path
        db.session.commit()
    except Exception as e:
        flash(f'Producto creado pero hubo un error al generar el QR: {str(e)}', 'warning')
    
    flash('Producto creado exitosamente', 'success')
    return redirect(url_for('productos.index'))

@productos_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    from models.historial_precio import HistorialPrecio
    product = Producto.query.get_or_404(id)
    
    code = request.form.get('code')
    name = request.form.get('name')
    
    if not code or not name:
        flash('El código y el nombre son obligatorios', 'danger')
        return redirect(url_for('productos.index'))
    
    # Check if code is being changed and if new code already exists
    if code != product.code:
        existing = Producto.query.filter_by(code=code).first()
        if existing:
            flash('Ya existe un producto con ese código', 'warning')
            return redirect(url_for('productos.index'))
    
    # Check serial number
    serial_number = request.form.get('serial_number')
    if serial_number and serial_number != product.serial_number:
        existing_serial = Producto.query.filter_by(serial_number=serial_number).first()
        if existing_serial:
            flash('Ya existe un producto con ese número de serie', 'warning')
            return redirect(url_for('productos.index'))
    
    # Update product
    product.code = code
    product.name = name
    product.description = request.form.get('description')
    product.brand = request.form.get('brand')
    product.model = request.form.get('model')
    product.serial_number = serial_number
    product.status = request.form.get('status', 'disponible')
    product.current_stock = request.form.get('current_stock', 0, type=int)
    product.min_stock = request.form.get('min_stock', 0, type=int)
    product.location = request.form.get('location')
    new_price = request.form.get('reference_price', type=float)
    
    # Record price history if changed
    if new_price is not None and (product.reference_price is None or abs(float(product.reference_price) - new_price) > 0.01):
        history = HistorialPrecio(product_id=product.id, price=new_price)
        db.session.add(history)
        product.last_price_update = datetime.utcnow()
    
    product.reference_price = new_price
    product.notes = request.form.get('notes')
    product.ip_address = request.form.get('ip_address')
    
    parent_id = request.form.get('parent_id', type=int)
    product.parent_id = parent_id if parent_id and parent_id != product.id else None
    
    category_id = request.form.get('category_id', type=int)
    supplier_id = request.form.get('supplier_id', type=int)
    product.category_id = category_id if category_id else None
    product.supplier_id = supplier_id if supplier_id else None
    
    # Regenerate QR if code changed
    if code != product.code:
        try:
            qr_path = generate_qr_code(product.id, product.code)
            product.qr_code_path = qr_path
        except Exception as e:
            flash(f'Producto actualizado pero hubo un error al generar el QR: {str(e)}', 'warning')
    
    db.session.commit()
    flash('Producto actualizado exitosamente', 'success')
    return redirect(url_for('productos.index'))

@productos_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    product = Producto.query.get_or_404(id)
    
    # Check if product has movements
    if product.movimientos.count() > 0:
        flash('No se puede eliminar: tiene movimientos de stock asociados', 'danger')
        return redirect(url_for('productos.index'))
    
    # Delete QR code file if exists
    if product.qr_code_path:
        qr_file = os.path.join('static', product.qr_code_path)
        if os.path.exists(qr_file):
            try:
                os.remove(qr_file)
            except:
                pass
    
    db.session.delete(product)
    db.session.commit()
    flash('Producto eliminado exitosamente', 'success')
    return redirect(url_for('productos.index'))

@productos_bp.route('/download-qr/<int:id>')
@login_required
def download_qr(id):
    product = Producto.query.get_or_404(id)
    
    if not product.qr_code_path:
        flash('Este producto no tiene código QR generado', 'warning')
        return redirect(url_for('productos.index'))
    
    qr_file = os.path.join('static', product.qr_code_path)
    if not os.path.exists(qr_file):
        flash('El archivo QR no existe', 'danger')
        return redirect(url_for('productos.index'))
    
    return send_file(qr_file, as_attachment=True, download_name=f'QR_{product.code}.png')
