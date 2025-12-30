from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from models.product import Product
from models.loan import Loan

dashboard_bp = Blueprint('dashboard', __name__)

from models.category import Category
from models.supplier import Supplier

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Métricas para el Dashboard
    total_products = Product.query.count()
    low_stock_count = Product.query.filter(Product.current_stock <= Product.min_stock).count()
    active_loans = Loan.query.filter_by(status='active').count()
    total_categories = Category.query.count()
    total_suppliers = Supplier.query.count()
    
    # Productos recientes (últimos 5)
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(5).all()

    return render_template('dashboard/index.html', 
                           total_products=total_products,
                           low_stock_count=low_stock_count,
                           active_loans=active_loans,
                           total_categories=total_categories,
                           total_suppliers=total_suppliers,
                           recent_products=recent_products)
