from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    color = db.Column(db.String(7), default='#3b82f6')  # Hex color for UI badges
    icon = db.Column(db.String(50), default='box')      # Icon name (e.g., FontAwesome)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    # Relaciones
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon
        }

    @property
    def parents_path(self):
        """Returns a list of parent categories up to the root, ordered from root to immediate parent."""
        parents = []
        current = self.parent
        while current:
            parents.insert(0, current)
            current = current.parent
        return parents
