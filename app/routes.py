from flask import Blueprint, request, jsonify
from app.models import User, Order
from app import db

bp = Blueprint('main', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(username=data['username'], role=data['role'], location=data['location'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/order', methods=['POST'])
def create_order():
    data = request.get_json()
    order = Order(service_type=data['service_type'], client_id=data['client_id'])
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'Order created successfully'}), 201 