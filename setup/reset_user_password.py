#!/usr/bin/env python3
"""
User Password Reset Utility
============================

This script allows you to reset passwords for any user account (admin or normal users).
Run this script from the command line to reset user passwords.

Usage:
    python reset_user_password.py

The script will:
1. Allow you to choose between admin users, normal users, or all users
2. Show users based on your selection
3. Allow you to select which user to reset
4. Set a new password for the selected user
"""

import sys
import os
from getpass import getpass

# Add the parent directory to Python path to import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from flask import Flask
from config import Config
from models import db, User

def create_app():
    """Create and configure Flask app for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def get_users_by_type(user_type="all"):
    """Get users from the database based on type."""
    if user_type == "admin":
        return User.query.filter_by(is_admin=True).all()
    elif user_type == "normal":
        return User.query.filter_by(is_admin=False).all()
    else:  # all users
        return User.query.all()

def display_users(users, user_type="users"):
    """Display a list of users."""
    print(f"\n{user_type.title()}:")
    print("-" * 50)
    for i, user in enumerate(users, 1):
        user_role = " (Admin)" if user.is_admin else " (User)"
        status = " [INACTIVE]" if not user.is_active else ""
        print(f"{i}. {user.username}{user_role} ({user.first_name} {user.last_name}) - {user.email}{status}")
    print("-" * 50)

def get_user_type_choice():
    """Get user's choice for which type of users to display."""
    print("\nUser Type Options:")
    print("1. Admin users only")
    print("2. Normal users only") 
    print("3. All users")
    
    while True:
        try:
            choice = int(input("\nSelect user type to display (1-3): "))
            if choice == 1:
                return "admin"
            elif choice == 2:
                return "normal"
            elif choice == 3:
                return "all"
            else:
                print("Invalid selection. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def reset_password(user, new_password):
    """Reset the password for a user."""
    try:
        user.set_password(new_password)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error resetting password: {e}")
        return False

def main():
    """Main function to run the password reset utility."""
    print("=" * 60)
    print("IGD Support User Password Reset Utility")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Get user type choice
        user_type = get_user_type_choice()
        
        # Get users based on selection
        users = get_users_by_type(user_type)
        
        if not users:
            print(f"No {user_type} users found in the database.")
            return
        
        # Display users
        display_users(users, f"{user_type} users" if user_type != "all" else "users")
        
        # Get user selection
        try:
            choice = int(input(f"\nSelect user to reset password (1-{len(users)}): "))
            if choice < 1 or choice > len(users):
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        
        selected_user = users[choice - 1]
        user_role = "Admin" if selected_user.is_admin else "User"
        print(f"\nSelected: {selected_user.username} ({user_role}) - {selected_user.first_name} {selected_user.last_name}")
        
        # Show warning if user is inactive
        if not selected_user.is_active:
            print("⚠️  WARNING: This user account is currently INACTIVE!")
            reactivate = input("Do you want to reactivate this account? (y/N): ")
            if reactivate.lower() == 'y':
                selected_user.is_active = True
                print("Account will be reactivated after password reset.")
        
        # Confirm the action
        confirm = input(f"Are you sure you want to reset password for {selected_user.username}? (y/N): ")
        if confirm.lower() != 'y':
            print("Password reset cancelled.")
            return
        
        # Get new password
        print("\nEnter new password:")
        new_password = getpass("New password: ")
        confirm_password = getpass("Confirm password: ")
        
        if new_password != confirm_password:
            print("Passwords do not match!")
            return
        
        if len(new_password) < 6:
            print("Password must be at least 6 characters long!")
            return
        
        # Reset the password
        if reset_password(selected_user, new_password):
            print(f"\nPassword successfully reset for {selected_user.username}!")
            print("The user can now log in with the new password.")
        else:
            print("Failed to reset password. Please check the error message above.")

if __name__ == "__main__":
    main()
