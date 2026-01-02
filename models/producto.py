from app import db
from datetime import datetime

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    serial_number = db.Column(db.String(100), unique=True)
    
    # Status: 'en_uso', 'disponible', 'prestado', 'mantenimiento', 'baja'
    status = db.Column(db.String(20), default='disponible')
    
    # Condition: 'nuevo', 'usado'
    condition = db.Column(db.String(10), default='nuevo')
    
    current_stock = db.Column(db.Integer, default=0)
    min_stock = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100))
    
    # Precios
    reference_price = db.Column(db.Numeric(10, 2))
    last_price_update = db.Column(db.DateTime)
    is_price_estimated = db.Column(db.Boolean, default=False)
    
    qr_code_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    
    # Seguimiento de IP y Componentes
    ip_address = db.Column(db.String(45)) # Soporta IPv6
    parent_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    
    # Nuevos campos Fase 10/11
    fecha_fin_vida_util = db.Column(db.Date) # Para búsquedas por fecha
    precio_dolar = db.Column(db.Numeric(10, 2))
    image_path = db.Column(db.String(255)) # Ruta relativa a static/uploads/productos
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('categorias.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    movimientos = db.relationship('MovimientoStock', backref='producto', lazy='dynamic')
    prestamos = db.relationship('Prestamo', backref='producto', lazy='dynamic')
    
    # Relación para componentes (auto-referencia)
    componentes = db.relationship('Producto', 
                                backref=db.backref('equipo_padre', remote_side=[id]),
                                lazy='dynamic')

    # Nota: La relación con compras se maneja a través de PurchaseItem.product

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'status': self.status,
            'stock': self.current_stock,
            'category': self.category.name if self.category else None
        }
