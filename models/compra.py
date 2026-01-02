from app import db
from datetime import datetime

class Compra(db.Model):
    __tablename__ = 'compras'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status: 'pendiente', 'verificada'
    status = db.Column(db.String(20), default='pendiente')
    
    # Totales de la factura
    total_without_vat = db.Column(db.Numeric(10, 2), default=0)
    total_with_vat = db.Column(db.Numeric(10, 2), default=0)
    
    payment_method = db.Column(db.String(50)) # E.g., 'Efectivo', 'Transferencia', 'Cheque'
    notes = db.Column(db.Text)
    
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    items = db.relationship('ItemCompra', backref='compra', cascade='all, delete-orphan')
    proveedor = db.relationship('Proveedor', backref=db.backref('compras', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'supplier': self.proveedor.name if self.proveedor else 'N/A',
            'date': self.purchase_date.strftime('%d/%m/%Y'),
            'total': str(self.total_with_vat),
            'items_count': len(self.items)
        }
