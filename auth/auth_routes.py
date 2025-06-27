from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models import db, User
from .auth_utils import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.is_json:
            # API endpoint
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            # Form submission
            username = request.form.get('username')
            password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            if request.is_json:
                return jsonify({
                    'message': 'Login successful',
                    'user': user.to_dict()
                }), 200
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
        else:
            if request.is_json:
                return jsonify({'error': 'Invalid username or password'}), 401
            else:
                flash('Invalid username or password', 'error')
                return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.is_json:
        return jsonify({'message': 'Logout successful'}), 200
    else:
        flash('You have been logged out', 'info')
        return redirect(url_for('home'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if request.is_json:
            # API endpoint
            data = request.get_json()
        else:
            # Form submission
            data = request.form.to_dict()
        
        try:
            # Check if user already exists
            existing_user = User.query.filter(
                (User.username == data['username']) | 
                (User.email == data['email'])
            ).first()
            
            if existing_user:
                error_msg = 'Username or email already exists'
                if request.is_json:
                    return jsonify({'error': error_msg}), 400
                else:
                    flash(error_msg, 'error')
                    return render_template('auth/register.html')
            
            user = User(
                username=data['username'],
                email=data['email'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'message': 'Registration successful',
                    'user': user.to_dict()
                }), 201
            else:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('auth.login'))
                
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 400
            else:
                flash('Registration failed. Please try again.', 'error')
                return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/profile')
@login_required
def profile():
    from .auth_utils import get_current_user
    user = get_current_user()
    if request.is_json:
        return jsonify(user.to_dict())
    return render_template('auth/profile.html', user=user)