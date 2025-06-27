from functools import wraps
from flask import session, jsonify, request, redirect, url_for, flash
from models import User
import logging

logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Checking authentication for {f.__name__}")
        logger.info(f"Session contents: {dict(session)}")
        
        if 'user_id' not in session:
            logger.warning(f"No user_id in session for {f.__name__}")
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            else:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
        
        logger.info(f"User {session['user_id']} authenticated for {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.info(f"Checking admin authentication for {f.__name__}")
        
        if 'user_id' not in session:
            logger.warning(f"No user_id in session for admin endpoint {f.__name__}")
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            else:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
        
        user = get_current_user()
        if not user or not user.is_admin:
            logger.warning(f"User {session.get('user_id')} lacks admin privileges for {f.__name__}")
            if request.is_json:
                return jsonify({'error': 'Admin privileges required'}), 403
            else:
                flash('Admin privileges required to access this page.', 'error')
                return redirect(url_for('home'))
        
        logger.info(f"Admin user {user.id} authenticated for {f.__name__}")
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            logger.info(f"Getting user for session user_id: {user_id}")
            user = User.query.get(user_id)
            if user:
                logger.info(f"Found user: {user.username} (id: {user.id})")
            else:
                logger.warning(f"No user found for user_id: {user_id}")
            return user
        else:
            logger.info("No user_id in session")
            return None
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}")
        return None