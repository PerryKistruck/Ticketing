# TicketPro - Advanced Ticketing System

A comprehensive web-based ticketing system built with Flask, featuring role-based access control and administrative capabilities.

## 🌟 Features

### Core Functionality
- **Ticket Management**: Create, view, edit, and track support tickets
- **User Authentication**: Secure login/logout with session management  
- **Responsive Design**: Modern Bootstrap-based UI that works on all devices
- **Real-time Updates**: Dynamic dashboard with live ticket statistics

### Administrator Features ⭐ NEW
- **Admin Dashboard**: Dedicated interface for managing all system tickets
- **Ticket Assignment**: Assign tickets to administrators for handling
- **User Role Management**: Designate users as administrators
- **Advanced Permissions**: Admins can view, edit, assign, and delete any ticket
- **System Statistics**: Comprehensive reporting and analytics

### User Roles
- **Regular Users**: Can create and manage their own tickets
- **Administrators**: Full system access with ticket management capabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for development)
- Virtual environment (recommended)

### Installation
1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment: `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Set up the database (see Database Setup below)
6. Create your first admin user: `python create_admin.py admin admin@example.com password123 Admin User`
7. Run the application: `python main.py`

### Database Setup
- For PostgreSQL: Run `setup/database_setup.sql` and then `setup/admin_migration.sql`
- For SQLite: The app will create tables automatically on first run

## 📱 Usage

### For Regular Users
1. Register an account or log in
2. Access your dashboard to view your tickets
3. Create new tickets using the "New Ticket" button
4. Edit your own tickets as needed

### For Administrators
1. Log in with an admin account
2. Access the admin dashboard via the crown icon in navigation
3. View all system tickets with advanced filtering
4. Assign tickets to yourself or other administrators
5. Manage ticket status, priority, and resolution

## 🔧 Technical Details

### Architecture
- **Backend**: Flask (Python)
- **Frontend**: Bootstrap 5, JavaScript (ES6)
- **Database**: PostgreSQL/SQLite with SQLAlchemy ORM
- **Authentication**: Session-based with password hashing

### Key Files
- `main.py` - Application entry point and routes
- `models.py` - Database models and relationships
- `auth/` - Authentication and authorization logic
- `routes/` - API endpoints for ticket operations
- `templates/` - HTML templates with Jinja2
- `static/` - CSS, JavaScript, and assets

## 🔐 Security Features
- Password hashing with Werkzeug
- Session-based authentication
- Role-based access control
- SQL injection protection via ORM
- CSRF protection on forms
- Input validation and sanitization

## 📖 API Documentation
See `ADMIN_FEATURES.md` for detailed API endpoint documentation and admin feature specifications.

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support
For support and questions:
- Check the documentation in `ADMIN_FEATURES.md`
- Review the setup scripts in the `setup/` directory
- Contact your system administrator for access issues
