from app import db
from datetime import datetime

class MovimientoStock(db.Model):
    __tablename__ = 'movimientos_stock'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # type: 'entry', 'exit', 'adjustment'
    movement_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(200))
    reference = db.Column(db.String(100)) # e.g., Purchase Invoice ID or Loan ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
