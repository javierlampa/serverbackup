from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required
from app import db
from models.product import Product
from models.category import Category
from models.supplier import Supplier
from utils.qr_generator import generate_qr_code
from datetime import datetime
import os

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required
def index():
    # Get filter parameters
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    supplier_id = request.args.get('supplier_id', type=int)
    
    # Base query
    query = Product.query
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if status:
        query = query.filter_by(status=status)
    if supplier_id:
        query = query.filter_by(supplier_id=supplier_id)
    
    # Get all products
    products = query.order_by(Product.name).all()
    
    # Get all categories and suppliers for filters
    categories = Category.query.order_by(Category.name).all()
    suppliers = Supplier.query.order_by(Supplier.name).all()
    
    return render_template('products/index.html', 
                         products=products,
                         categories=categories,
                         suppliers=suppliers,
                         selected_category=category_id,
                         selected_status=status,
                         selected_supplier=supplier_id)

@products_bp.route('/add', methods=['POST'])
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
    
    if not code or not name:
        flash('El código y el nombre son obligatorios', 'danger')
        return redirect(url_for('products.index'))
    
    # Check if code already exists
    existing = Product.query.filter_by(code=code).first()
    if existing:
        flash('Ya existe un producto con ese código', 'warning')
        return redirect(url_for('products.index'))
    
    # Check if serial number already exists (if provided)
    if serial_number:
        existing_serial = Product.query.filter_by(serial_number=serial_number).first()
        if existing_serial:
            flash('Ya existe un producto con ese número de serie', 'warning')
            return redirect(url_for('products.index'))
    
    # Create product
    new_product = Product(
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
        supplier_id=supplier_id if supplier_id else None
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
    return redirect(url_for('products.index'))

@products_bp.route('/edit/<int:id>', methods=['POST'])
@login_required
def edit(id):
    product = Product.query.get_or_404(id)
    
    code = request.form.get('code')
    name = request.form.get('name')
    
    if not code or not name:
        flash('El código y el nombre son obligatorios', 'danger')
        return redirect(url_for('products.index'))
    
    # Check if code is being changed and if new code already exists
    if code != product.code:
        existing = Product.query.filter_by(code=code).first()
        if existing:
            flash('Ya existe un producto con ese código', 'warning')
            return redirect(url_for('products.index'))
    
    # Check serial number
    serial_number = request.form.get('serial_number')
    if serial_number and serial_number != product.serial_number:
        existing_serial = Product.query.filter_by(serial_number=serial_number).first()
        if existing_serial:
            flash('Ya existe un producto con ese número de serie', 'warning')
            return redirect(url_for('products.index'))
    
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
    product.reference_price = request.form.get('reference_price', type=float)
    product.notes = request.form.get('notes')
    
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
    return redirect(url_for('products.index'))

@products_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    product = Product.query.get_or_404(id)
    
    # Check if product has movements
    if product.movements.count() > 0:
        flash('No se puede eliminar: tiene movimientos de stock asociados', 'danger')
        return redirect(url_for('products.index'))
    
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
    return redirect(url_for('products.index'))

@products_bp.route('/download-qr/<int:id>')
@login_required
def download_qr(id):
    product = Product.query.get_or_404(id)
    
    if not product.qr_code_path:
        flash('Este producto no tiene código QR generado', 'warning')
        return redirect(url_for('products.index'))
    
    qr_file = os.path.join('static', product.qr_code_path)
    if not os.path.exists(qr_file):
        flash('El archivo QR no existe', 'danger')
        return redirect(url_for('products.index'))
    
    return send_file(qr_file, as_attachment=True, download_name=f'QR_{product.code}.png')
