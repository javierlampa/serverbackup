from app import db
from datetime import datetime

class Prestamo(db.Model):
    __tablename__ = 'prestamos'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    
    borrower_name = db.Column(db.String(100), nullable=False)
    borrower_contact = db.Column(db.String(100))
    
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_return_date = db.Column(db.Date)
    return_date = db.Column(db.DateTime)
    
    # Status: 'active', 'returned'
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)
    signature = db.Column(db.Text) # Base64 signature
    
    created_by = db.Column(db.Integer, db.ForeignKey('usuarios.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'product': self.product.name,
            'borrower': self.borrower_name,
            'loan_date': self.loan_date.isoformat(),
            'status': self.status
        }
