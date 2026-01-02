from datetime import datetime
from app import db

class Mantenimiento(db.Model):
    __tablename__ = 'mantenimientos'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False) # Preventivo, Correctivo, Garantía
    descripcion = db.Column(db.Text, nullable=False)
    costo = db.Column(db.Numeric(10, 2), default=0.00)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    estado = db.Column(db.String(20), default='en_proceso') # en_proceso, completado, cancelado
    tecnico = db.Column(db.String(100))
    
    # Relación con Producto
    producto = db.relationship('Producto', backref=db.backref('mantenimientos', lazy='dynamic'))

    def __repr__(self):
        return f'<Mantenimiento {self.id} - Producto {self.producto_id}>'
