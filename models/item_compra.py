from app import db

class ItemCompra(db.Model):
    __tablename__ = 'items_compra'

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Subtotales
    total_without_vat = db.Column(db.Numeric(10, 2), nullable=False)
    total_with_vat = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relaciones
    producto = db.relationship('Producto', backref=db.backref('items_compra', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.producto.name,
            'quantity': self.quantity,
            'unit_price': str(self.unit_price),
            'total_without_vat': str(self.total_without_vat),
            'total_with_vat': str(self.total_with_vat)
        }
