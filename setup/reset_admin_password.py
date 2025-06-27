#!/usr/bin/env python3
"""
Admin Password Reset Utility
============================

This script allows you to reset passwords for admin accounts.
Run this script from the command line to reset admin passwords.

Usage:
    python reset_admin_password.py

The script will:
1. Show all admin users
2. Allow you to select which admin to reset
3. Set a new password for the selected admin
"""

import sys
import os
from getpass import getpass

# Add the current directory to Python path to import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from config import Config
from models import db, User

def create_app():
    """Create and configure Flask app for database operations."""
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def get_admin_users():
    """Get all admin users from the database."""
    return User.query.filter_by(is_admin=True).all()

def display_admin_users(admin_users):
    """Display a list of admin users."""
    print("\nAdmin Users:")
    print("-" * 50)
    for i, user in enumerate(admin_users, 1):
        print(f"{i}. {user.username} ({user.first_name} {user.last_name}) - {user.email}")
    print("-" * 50)

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
    print("TicketPro Admin Password Reset Utility")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Get all admin users
        admin_users = get_admin_users()
        
        if not admin_users:
            print("No admin users found in the database.")
            return
        
        # Display admin users
        display_admin_users(admin_users)
        
        # Get user selection
        try:
            choice = int(input(f"\nSelect admin user to reset password (1-{len(admin_users)}): "))
            if choice < 1 or choice > len(admin_users):
                print("Invalid selection.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        
        selected_user = admin_users[choice - 1]
        print(f"\nSelected: {selected_user.username} ({selected_user.first_name} {selected_user.last_name})")
        
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
            print("The admin can now log in with the new password.")
        else:
            print("Failed to reset password. Please check the error message above.")

if __name__ == "__main__":
    main()
