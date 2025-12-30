from flask import Blueprint, render_template
from flask_login import login_required
from models.movimiento_stock import MovimientoStock
from models.producto import Producto
from app import db

movimientos_bp = Blueprint('movimientos', __name__, url_prefix='/movimientos')

@movimientos_bp.route('/')
@login_required
def index():
    # Obtener todos los movimientos ordenados por fecha descendente
    movements = MovimientoStock.query.order_by(MovimientoStock.created_at.desc()).all()
    return render_template('movimientos/index.html', movements=movements)
