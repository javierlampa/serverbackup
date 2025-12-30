from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models.compra import Compra
from models.item_compra import ItemCompra
from models.producto import Producto
from models.proveedor import Proveedor
from models.movimiento_stock import MovimientoStock
from models.categoria import Categoria
from datetime import datetime
import json

compras_bp = Blueprint('compras', __name__, url_prefix='/compras')

@compras_bp.route('/')
@login_required
def index():
    purchases = Compra.query.order_by(Compra.purchase_date.desc()).all()
    return render_template('compras/index.html', purchases=purchases)

@compras_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        try:
            supplier_id = request.form.get('supplier_id')
            invoice_number = request.form.get('invoice_number')
            purchase_date_str = request.form.get('purchase_date')
            notes = request.form.get('notes')
            payment_method = request.form.get('payment_method')
            
            # Totales generales
            total_without_vat = float(request.form.get('total_without_vat', 0))
            total_with_vat = float(request.form.get('total_with_vat', 0))
            
            # Procesar items (vienen como JSON string desde el frontend)
            items_json = request.form.get('items_data')
            items_data = json.loads(items_json)
            
            if not items_data:
                flash('La factura debe tener al menos un producto', 'danger')
                return redirect(url_for('compras.create'))

            # Crear cabecera
            purchase = Compra(
                supplier_id=supplier_id,
                invoice_number=invoice_number,
                purchase_date=datetime.strptime(purchase_date_str, '%Y-%m-%d') if purchase_date_str else datetime.utcnow(),
                total_without_vat=total_without_vat,
                total_with_vat=total_with_vat,
                payment_method=payment_method,
                notes=notes,
                created_by=current_user.id
            )
            
            db.session.add(purchase)
            db.session.flush() # Para obtener el ID de la factura
            
            # Crear items y actualizar stock
            for item in items_data:
                product_id = item['product_id']
                quantity = int(item['quantity'])
                unit_price = float(item['unit_price'])
                item_total_without_vat = float(item['total_without_vat'])
                item_total_with_vat = float(item['total_with_vat'])
                
                # Crear item de factura
                purchase_item = ItemCompra(
                    purchase_id=purchase.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_without_vat=item_total_without_vat,
                    total_with_vat=item_total_with_vat
                )
                db.session.add(purchase_item)
                
                # Actualizar stock del producto
                product = Producto.query.get(product_id)
                if product:
                    old_stock = product.current_stock
                    product.current_stock += quantity
                    
                    # Registrar movimiento de stock
                    movement = MovimientoStock(
                        product_id=product.id,
                        movement_type='entry',
                        quantity=quantity,
                        reason=f'Compra - Factura {invoice_number}',
                        user_id=current_user.id
                    )
                    db.session.add(movement)
            
            db.session.commit()
            flash('Factura de compra registrada exitosamente y stock actualizado', 'success')
            return redirect(url_for('compras.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la factura: {str(e)}', 'danger')
            return redirect(url_for('compras.create'))

    suppliers = Proveedor.query.all()
    products = Producto.query.all()
    categories = Categoria.query.all()
    return render_template('compras/create.html', 
                         suppliers=suppliers, 
                         products=products,
                         categories=categories,
                         today=datetime.utcnow().strftime('%Y-%m-%d'))

@compras_bp.route('/view/<int:id>')
@login_required
def view(id):
    purchase = Compra.query.get_or_404(id)
    return render_template('compras/view.html', purchase=purchase)
