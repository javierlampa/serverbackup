from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    recipient_phone = db.Column(db.String(20))
    message_body = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    product = db.relationship('Producto', backref='notifications')
