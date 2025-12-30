from app import db
from datetime import datetime

class PurchaseItem(db.Model):
    __tablename__ = 'purchase_items'

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Subtotales
    total_without_vat = db.Column(db.Numeric(10, 2), nullable=False)
    total_with_vat = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relaciones
    product = db.relationship('Product', backref=db.backref('purchase_items', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name,
            'quantity': self.quantity,
            'unit_price': str(self.unit_price),
            'total_without_vat': str(self.total_without_vat),
            'total_with_vat': str(self.total_with_vat)
        }
