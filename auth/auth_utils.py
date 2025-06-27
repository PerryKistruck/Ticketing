from functools import wraps
from flask import session, jsonify, request, redirect, url_for, flash
from models import User
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            else:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            else:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
        
        user = get_current_user()
        if not user or not user.is_admin:
            if request.is_json:
                return jsonify({'error': 'Admin privileges required'}), 403
            else:
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