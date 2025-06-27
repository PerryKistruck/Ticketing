from flask import Blueprint, request, jsonify
from models import db, User
from auth.auth_utils import login_required, get_current_user

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'])
@login_required
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users_bp.route('/users', methods=['POST'])
def create_user():
    # This endpoint is now mainly for admin use, regular users should use /register
    data = request.get_json()
    try:
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | 
            (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        if 'password' in data:
            user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    current_user = get_current_user()
    # Users can only view their own profile or all users if admin (simplified check)
    if current_user.id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@users_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    current_user = get_current_user()
    if current_user.id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    try:
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        
        if 'password' in data:
            user.set_password(data['password'])
        
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    current_user = get_current_user()
    if current_user.id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@users_bp.route('/users/<int:user_id>/tickets', methods=['GET'])
@login_required
def get_user_tickets(user_id):
    current_user = get_current_user()
    if current_user.id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    from models import Ticket
    user = User.query.get_or_404(user_id)
    tickets = Ticket.query.filter_by(user_id=user_id).all()
    return jsonify([ticket.to_dict() for ticket in tickets])