from app import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuit = db.Column(db.String(13))  # Formato: XX-XXXXXXXX-X
    contact_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    products = db.relationship('Product', backref='supplier', lazy='dynamic')
    # La relación con compras se define en el modelo Purchase

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'cuit': self.cuit,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone
        }
