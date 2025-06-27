# This file makes the routes directory a Python package
from .tickets import tickets_bp
from .users import users_bp
from auth import auth_bp

def register_routes(app):
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(tickets_bp, url_prefix='/api/tickets')
    app.register_blueprint(users_bp, url_prefix='/api/users')
