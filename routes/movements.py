from flask import Blueprint, render_template
from flask_login import login_required
from models.stock_movement import StockMovement
from models.product import Product
from app import db

movements_bp = Blueprint('movements', __name__, url_prefix='/movements')

@movements_bp.route('/')
@login_required
def index():
    # Obtener todos los movimientos ordenados por fecha descendente
    movements = StockMovement.query.order_by(StockMovement.created_at.desc()).all()
    return render_template('movements/index.html', movements=movements)
