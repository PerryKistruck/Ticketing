# IGD Support System

A Flask-based web application for support ticket management with role-based access control.
Currently live on: https://perrylk.uk/

## Features

- Ticket management (CRUD operations)
- User authentication and authorization
- Administrative dashboard and controls
- Role-based permissions (users and administrators)
- Bootstrap-responsive interface

## Local instance Installation

### Prerequisites
- Python 3.11+
- PostgreSQL or SQLite
- Virtual environment

### Setup
1. Clone repository
2. Create virtual environment: `python -m venv .venv`
3. Activate environment: `.venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure database (run SQL scripts in `setup/`)
6. Create admin user: `python create_admin.py admin admin@example.com password123 "Admin User"`
7. Start application: `python main.py`

## Usage

### Getting Started
1. **Access the website**: Navigate to `http://localhost:5000` in your web browser after starting the application
2. **Create an account**: Click "Register" and fill in your details (username, email, password, full name)
3. **Login**: Use your credentials to access your personal dashboard

### For Regular Users

#### Creating a Support Ticket
1. **Login** to your account
2. **Click "Create New Ticket"** button on your dashboard
3. **Fill in the form**:
   - Enter a clear, descriptive title
   - Provide detailed description of your issue
   - Select priority level (Low, Medium, High, Critical)
4. **Submit** your ticket - you'll receive a confirmation

#### Managing Your Tickets
- **View tickets**: See all your tickets on the dashboard with status indicators
- **Edit tickets**: Click on any ticket to update details or add comments
- **Track progress**: Monitor status changes (Open → In Progress → Resolved → Closed)
- **Update information**: Modify ticket details as needed

### For Administrators

#### Admin Dashboard Access
1. **Login** with administrator credentials
2. **Navigate** to the admin dashboard (additional menu options will appear)
3. **View system overview**: See all tickets across all users

#### Managing All Tickets
- **Assign tickets**: Assign tickets to specific team members
- **Update status**: Change ticket status and priority
- **Bulk operations**: Manage multiple tickets simultaneously
- **User management**: View and manage user accounts and permissions

### Quick Tips
- **Ticket Status Guide**:
  - 🔴 **Open**: New ticket awaiting attention
  - 🟡 **In Progress**: Currently being worked on
  - 🟢 **Resolved**: Issue fixed, awaiting user confirmation
  - ⚫ **Closed**: Ticket completed and closed
- **Priority Levels**: Use appropriate priority (Critical for urgent issues, Low for minor requests)
- **Clear descriptions**: Provide as much detail as possible for faster resolution

## Architecture

- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: PostgreSQL/SQLite
- **Authentication**: Session-based with password hashing
- **Security**: Role-based access control, input validation

## Project Structure

- `main.py` - Application entry point
- `models.py` - Database models
- `auth/` - Authentication modules
- `routes/` - API endpoints
- `templates/` - HTML templates
- `static/` - Frontend assets
- `_test/` - Test suite
