# IGD Support System

A Flask-based web application for support ticket management with role-based access control.

## Features

- Ticket management (CRUD operations)
- User authentication and authorization
- Administrative dashboard and controls
- Role-based permissions (users and administrators)
- Bootstrap-responsive interface

## Installation

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

### Users
- Register/login to access personal dashboard
- Create and manage personal tickets
- Edit ticket details and status

### Administrators  
- Access admin dashboard for system-wide ticket management
- Assign tickets and manage user roles
- Perform administrative operations on all tickets

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
