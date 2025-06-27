from flask import Blueprint, request, jsonify
from models import db, Ticket, User
from auth.auth_utils import login_required, get_current_user, admin_required

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route('/', methods=['GET'])
@login_required
def get_tickets():
    current_user = get_current_user()
    
    # This endpoint always shows only personal tickets (created by user OR assigned to user)
    # Even for admins when they're using the regular dashboard
    tickets = Ticket.query.filter(
        (Ticket.user_id == current_user.id) | 
        (Ticket.assigned_to == current_user.id)
    ).all()
    
    return jsonify([ticket.to_dict() for ticket in tickets])

@tickets_bp.route('/admin/all', methods=['GET'])
@admin_required
def get_all_tickets():
    """Admin endpoint to get all tickets with filtering options"""
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    assigned_to_filter = request.args.get('assigned_to')
    
    query = Ticket.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if assigned_to_filter:
        query = query.filter_by(assigned_to=assigned_to_filter)
    
    tickets = query.all()
    return jsonify([ticket.to_dict() for ticket in tickets])

@tickets_bp.route('/admin/assign/<int:ticket_id>', methods=['PUT'])
@admin_required
def assign_ticket(ticket_id):
    """Admin endpoint to assign tickets to users"""
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()
    
    assigned_to = data.get('assigned_to')
    if assigned_to:
        # Verify the assigned user exists and is an admin
        assignee = User.query.get(assigned_to)
        if not assignee or not assignee.is_admin:
            return jsonify({'error': 'Can only assign tickets to admin users'}), 400
        
        ticket.assigned_to = assigned_to
    else:
        ticket.assigned_to = None
    
    try:
        db.session.commit()
        return jsonify(ticket.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@tickets_bp.route('/', methods=['POST'])
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

@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
@login_required
def get_ticket(ticket_id):
    current_user = get_current_user()
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Admins can view any ticket, users can view tickets they created or are assigned to
    if not current_user.is_admin and ticket.user_id != current_user.id and ticket.assigned_to != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    return jsonify(ticket.to_dict())

@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
@login_required
def update_ticket(ticket_id):
    current_user = get_current_user()
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Admins can update any ticket, users can update tickets they created or are assigned to
    if not current_user.is_admin and ticket.user_id != current_user.id and ticket.assigned_to != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    try:
        ticket.title = data.get('title', ticket.title)
        ticket.description = data.get('description', ticket.description)
        
        # Only admins can change status
        if current_user.is_admin and 'status' in data:
            ticket.status = data.get('status', ticket.status)
        
        ticket.priority = data.get('priority', ticket.priority)
        
        # Only admins can change assignment
        if current_user.is_admin and 'assigned_to' in data:
            assigned_to = data.get('assigned_to')
            if assigned_to:
                assignee = User.query.get(assigned_to)
                if not assignee or not assignee.is_admin:
                    return jsonify({'error': 'Can only assign tickets to admin users'}), 400
            ticket.assigned_to = assigned_to
        
        db.session.commit()
        return jsonify(ticket.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    current_user = get_current_user()
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Only admins can delete tickets
    if not current_user.is_admin:
        return jsonify({'error': 'Admin privileges required to delete tickets'}), 403
    
    try:
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({'message': 'Ticket deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@tickets_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_admin_users():
    """Get all admin users for ticket assignment"""
    admin_users = User.query.filter_by(is_admin=True, is_active=True).all()
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'full_name': f"{user.first_name} {user.last_name}"
    } for user in admin_users])