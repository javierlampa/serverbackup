from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'

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
    
    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    movements = db.relationship('StockMovement', backref='product', lazy='dynamic')
    loans = db.relationship('Loan', backref='product', lazy='dynamic')
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
