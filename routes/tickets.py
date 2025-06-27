from flask import Blueprint, request, jsonify
from models import db, Ticket
from auth.auth_utils import login_required, get_current_user

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/tickets', methods=['GET'])
@login_required
def get_tickets():
    current_user = get_current_user()
    # Users can only see their own tickets
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@tickets_bp.route('/tickets', methods=['POST'])
@login_required
def create_ticket():
    current_user = get_current_user()
    data = request.get_json()
    try:
        ticket = Ticket(
            title=data['title'],
            description=data['description'],
            status=data.get('status', 'open'),
            priority=data.get('priority', 'medium'),
            user_id=current_user.id  # Always use current user's ID
        )
        db.session.add(ticket)
        db.session.commit()
        return jsonify(ticket.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@tickets_bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    current_user = get_current_user()
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Users can only view their own tickets
    if ticket.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(ticket.to_dict())

@tickets_bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
@login_required
def update_ticket(ticket_id):
    current_user = get_current_user()
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Users can only update their own tickets
    if ticket.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    try:
        ticket.title = data.get('title', ticket.title)
        ticket.description = data.get('description', ticket.description)
        ticket.status = data.get('status', ticket.status)
        ticket.priority = data.get('priority', ticket.priority)
        
        db.session.commit()
        return jsonify(ticket.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@tickets_bp.route('/tickets/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    current_user = get_current_user()
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Users can only delete their own tickets
    if ticket.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({'message': 'Ticket deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400