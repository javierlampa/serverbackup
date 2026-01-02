from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import db
from models.producto import Producto
from models.prestamo import Prestamo
from models.compra import Compra

dashboard_bp = Blueprint('dashboard', __name__)

from models.categoria import Categoria
from models.proveedor import Proveedor

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    # Métricas para el Dashboard
    total_products = Producto.query.count()
    low_stock_count = Producto.query.filter(Producto.current_stock <= Producto.min_stock).count()
    active_loans = Prestamo.query.filter_by(status='active').count()
    total_categories = Categoria.query.count()
    total_categories = Categoria.query.count()
    total_suppliers = Proveedor.query.count()
    
    # Alertas
    pending_purchases_count = Compra.query.filter_by(status='pendiente').count()
    
    # Productos recientes (últimos 5)
    recent_products = Producto.query.order_by(Producto.created_at.desc()).limit(5).all()

    return render_template('dashboard/index.html', 
                           total_products=total_products,
                           low_stock_count=low_stock_count,
                           active_loans=active_loans,
                           total_categories=total_categories,
                           total_suppliers=total_suppliers,
                           pending_purchases_count=pending_purchases_count,
                           recent_products=recent_products)
