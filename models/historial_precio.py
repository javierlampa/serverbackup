from app import db
from datetime import datetime

class HistorialPrecio(db.Model):
    __tablename__ = 'historial_precios'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación inversa se maneja vía backref en el modelo Producto o aquí
    producto = db.relationship('Producto', backref=db.backref('historial_precios', lazy='dynamic'))
