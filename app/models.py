from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'client' or 'contractor'
    location = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Float, default=0.0)
    max_orders_per_day = db.Column(db.Integer, default=2)

    def __repr__(self):
        return f'<User {self.username}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contractor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Order {self.id}>' 