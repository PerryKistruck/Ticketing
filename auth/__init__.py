# This file makes the auth directory a Python package
from .auth_routes import auth_bp
from .auth_utils import login_required, get_current_user

__all__ = ['auth_bp', 'login_required', 'get_current_user']
