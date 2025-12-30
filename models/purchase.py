from app import db
from datetime import datetime

class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    invoice_number = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Totales de la factura
    total_without_vat = db.Column(db.Numeric(10, 2), default=0)
    total_with_vat = db.Column(db.Numeric(10, 2), default=0)
    
    payment_method = db.Column(db.String(50)) # E.g., 'Efectivo', 'Transferencia', 'Cheque'
    notes = db.Column(db.Text)
    
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    items = db.relationship('PurchaseItem', backref='purchase', cascade='all, delete-orphan')
    supplier = db.relationship('Supplier', backref=db.backref('purchases', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'supplier': self.supplier.name if self.supplier else 'N/A',
            'date': self.purchase_date.strftime('%d/%m/%Y'),
            'total': str(self.total_with_vat),
            'items_count': len(self.items)
        }
