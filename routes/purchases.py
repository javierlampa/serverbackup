from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from models.purchase import Purchase
from models.purchase_item import PurchaseItem
from models.product import Product
from models.supplier import Supplier
from models.stock_movement import StockMovement
from datetime import datetime
import json

purchases_bp = Blueprint('purchases', __name__, url_prefix='/purchases')

@purchases_bp.route('/')
@login_required
def index():
    purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    return render_template('purchases/index.html', purchases=purchases)

@purchases_bp.route('/create', methods=['GET', 'POST'])
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
                return redirect(url_for('purchases.create'))

            # Crear cabecera
            purchase = Purchase(
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
                purchase_item = PurchaseItem(
                    purchase_id=purchase.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_without_vat=item_total_without_vat,
                    total_with_vat=item_total_with_vat
                )
                db.session.add(purchase_item)
                
                # Actualizar stock del producto
                product = Product.query.get(product_id)
                if product:
                    old_stock = product.current_stock
                    product.current_stock += quantity
                    
                    # Registrar movimiento de stock
                    movement = StockMovement(
                        product_id=product.id,
                        type='entrada',
                        quantity=quantity,
                        reason=f'Compra - Factura {invoice_number}',
                        user_id=current_user.id
                    )
                    db.session.add(movement)
            
            db.session.commit()
            flash('Factura de compra registrada exitosamente y stock actualizado', 'success')
            return redirect(url_for('purchases.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar la factura: {str(e)}', 'danger')
            return redirect(url_for('purchases.create'))

    suppliers = Supplier.query.all()
    products = Product.query.all()
    from models.category import Category
    categories = Category.query.all()
    return render_template('purchases/create.html', 
                         suppliers=suppliers, 
                         products=products,
                         categories=categories,
                         today=datetime.utcnow().strftime('%Y-%m-%d'))

@purchases_bp.route('/view/<int:id>')
@login_required
def view(id):
    purchase = Purchase.query.get_or_404(id)
    return render_template('purchases/view.html', purchase=purchase)
