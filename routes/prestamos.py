from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models.prestamo import Loan
from models.producto import Product
from models.movimiento_stock import StockMovement
from datetime import datetime

prestamos_bp = Blueprint('prestamos', __name__, url_prefix='/prestamos')

@prestamos_bp.route('/')
@login_required
def index():
    loans = Loan.query.order_by(Loan.loan_date.desc()).all()
    return render_template('prestamos/index.html', loans=loans)

@prestamos_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        borrower_name = request.form.get('borrower_name')
        borrower_contact = request.form.get('borrower_contact')
        loan_date_str = request.form.get('loan_date')
        expected_return_date_str = request.form.get('expected_return_date')
        notes = request.form.get('notes')
        signature = request.form.get('signature') # Base64 string
        
        product = Product.query.get_or_404(product_id)
        
        if product.current_stock <= 0:
            flash('No hay stock disponible para realizar el préstamo.', 'danger')
            return redirect(url_for('prestamos.create'))
            
        loan_date = datetime.utcnow()
        if loan_date_str:
            loan_date = datetime.strptime(loan_date_str, '%Y-%m-%d')

        expected_return_date = None
        if expected_return_date_str:
            expected_return_date = datetime.strptime(expected_return_date_str, '%Y-%m-%d').date()
            
        loan = Loan(
            product_id=product_id,
            borrower_name=borrower_name,
            borrower_contact=borrower_contact,
            loan_date=loan_date,
            expected_return_date=expected_return_date,
            notes=notes,
            signature=signature,
            created_by=current_user.id,
            status='active'
        )
        
        # Actualizar stock del producto
        product.current_stock -= 1
        
        # Registrar movimiento de stock
        movement = StockMovement(
            product_id=product_id,
            user_id=current_user.id,
            movement_type='exit',
            quantity=1,
            reason=f'Préstamo a {borrower_name}',
            reference=f'LOAN-{datetime.now().strftime("%Y%m%d%H%M")}'
        )
        
        db.session.add(loan)
        db.session.add(movement)
        db.session.commit()
        
        flash('Préstamo registrado correctamente.', 'success')
        return redirect(url_for('prestamos.index'))
        
    products = Product.query.filter(Product.current_stock > 0).all()
    return render_template('prestamos/create.html', products=products)

@prestamos_bp.route('/return/<int:id>', methods=['POST'])
@login_required
def return_loan(id):
    loan = Loan.query.get_or_404(id)
    
    if loan.status == 'returned':
        flash('Este préstamo ya fue devuelto.', 'warning')
        return redirect(url_for('prestamos.index'))
        
    loan.status = 'returned'
    loan.return_date = datetime.utcnow()
    
    # Actualizar stock del producto
    product = loan.product
    product.current_stock += 1
    
    # Registrar movimiento de stock
    movement = StockMovement(
        product_id=product.id,
        user_id=current_user.id,
        movement_type='entry',
        quantity=1,
        reason=f'Devolución de préstamo - {loan.borrower_name}',
        reference=f'RETURN-{id}'
    )
    
    db.session.add(movement)
    db.session.commit()
    
    flash('Producto devuelto correctamente.', 'success')
    return redirect(url_for('prestamos.index'))
