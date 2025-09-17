from functools import wraps
from flask import session, jsonify, request, redirect, url_for, flash
from models import User
import logging

logger = logging.getLogger(__name__)

def _is_api_request():
    # Treat as API if path starts with /api/ OR Accept header prefers JSON OR explicit JSON body
    if request.path.startswith('/api/'):
        return True
    accept = request.headers.get('Accept', '')
    if 'application/json' in accept.lower():
        return True
    if request.is_json:
        return True
    # X-Requested-With often used by AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    return False


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if _is_api_request():
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if _is_api_request():
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        user = get_current_user()
        if not user or not user.is_admin:
            if _is_api_request():
                return jsonify({'error': 'Admin privileges required'}), 403
            flash('Admin privileges required to access this page.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            return user
        return None
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        return None