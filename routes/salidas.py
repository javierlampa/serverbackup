from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models.producto import Producto
from models.prestamo import Prestamo
from models.movimiento_stock import MovimientoStock
from datetime import datetime

salidas_bp = Blueprint('salidas', __name__, url_prefix='/salidas')

@salidas_bp.route('/scan')
@login_required
def scan():
    # Obtener todos los productos para el buscador manual
    products = Producto.query.filter(Producto.current_stock > 0).all()
    return render_template('salidas/scan.html', products=products)

@salidas_bp.route('/process', methods=['POST'])
@login_required
def process():
    try:
        product_id = request.form.get('product_id')
        operation_type = request.form.get('operation_type') # 'loan' or 'exit'
        recipient_name = request.form.get('recipient_name')
        notes = request.form.get('notes')
        signature = request.form.get('signature') # Base64 string
        
        if not product_id or not operation_type or not recipient_name:
            flash('Faltan datos requeridos', 'danger')
            return redirect(url_for('salidas.scan'))
            
        product = Producto.query.get_or_404(product_id)
        
        if product.current_stock <= 0:
            flash(f'No hay stock disponible de {product.name}', 'danger')
            return redirect(url_for('salidas.scan'))
            
        # Descontar stock (común para ambos casos)
        product.current_stock -= 1
        
        if operation_type == 'loan':
            # Crear Préstamo
            loan = Prestamo(
                product_id=product.id,
                borrower_name=recipient_name,
                loan_date=datetime.utcnow(),
                notes=notes,
                signature=signature,
                created_by=current_user.id,
                status='active'
            )
            db.session.add(loan)
            
            # Movimiento de Stock
            movement = MovimientoStock(
                product_id=product.id,
                user_id=current_user.id,
                movement_type='exit',
                quantity=1,
                reason=f'Préstamo a {recipient_name}',
                reference=f'LOAN-QR-{datetime.now().strftime("%Y%m%d%H%M")}'
            )
            db.session.add(movement)
            flash(f'Préstamo registrado: {product.name} a {recipient_name}', 'success')
            
        elif operation_type == 'exit':
            # Solo Movimiento de Stock (Descarga/Consumo)
            movement = MovimientoStock(
                product_id=product.id,
                user_id=current_user.id,
                movement_type='exit',
                quantity=1,
                reason=f'Retirado por: {recipient_name} - {notes}',
                reference=f'EXIT-QR-{datetime.now().strftime("%Y%m%d%H%M")}',
                signature=signature
            )
            db.session.add(movement)
            flash(f'Salida registrada: {product.name} retirado por {recipient_name}', 'success')
            
        db.session.commit()
        return redirect(url_for('salidas.scan'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al procesar la operación: {str(e)}', 'danger')
        return redirect(url_for('salidas.scan'))

@salidas_bp.route('/get_product/<code_or_id>')
@login_required
def get_product(code_or_id):
    # Buscar por ID primero, luego por Código
    product = Producto.query.filter((Producto.id == code_or_id) | (Producto.code == code_or_id)).first()
    
    if product:
        return jsonify({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'code': product.code,
                'stock': product.current_stock,
                'image_path': product.image_path
            }
        })
    return jsonify({'success': False, 'message': 'Producto no encontrado'})
