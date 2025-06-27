-- TicketPro Database Setup Script for PostgreSQL
-- This script creates all necessary tables and indexes for the ticketing system

-- Create database (run this separately if needed)
-- CREATE DATABASE ticketpro;
-- \c ticketpro;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Add constraints
    CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_name_length CHECK (LENGTH(first_name) >= 1 AND LENGTH(last_name) >= 1)
);

-- Create Tickets table
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'medium',
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_tickets_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Check constraints for data integrity
    CONSTRAINT chk_status CHECK (status IN ('open', 'in_progress', 'closed', 'cancelled')),
    CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    CONSTRAINT chk_title_length CHECK (LENGTH(title) >= 1)
);

-- Create indexes for better performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_active ON users(is_active);

CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_updated_at ON tickets(updated_at);

-- Create composite indexes for common queries
CREATE INDEX idx_tickets_user_status ON tickets(user_id, status);
CREATE INDEX idx_tickets_user_priority ON tickets(user_id, priority);
CREATE INDEX idx_tickets_status_priority ON tickets(status, priority);
CREATE INDEX idx_tickets_user_created ON tickets(user_id, created_at DESC);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update the updated_at timestamp
CREATE TRIGGER update_tickets_updated_at 
    BEFORE UPDATE ON tickets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE VIEW ticket_summary AS
SELECT 
    t.id,
    t.title,
    t.status,
    t.priority,
    t.created_at,
    t.updated_at,
    u.username,
    u.first_name,
    u.last_name,
    u.email
FROM tickets t
JOIN users u ON t.user_id = u.id;

-- Create view for ticket statistics
CREATE VIEW ticket_stats AS
SELECT 
    COUNT(*) as total_tickets,
    COUNT(*) FILTER (WHERE status = 'open') as open_tickets,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tickets,
    COUNT(*) FILTER (WHERE status = 'closed') as closed_tickets,
    COUNT(*) FILTER (WHERE priority = 'high') as high_priority_tickets,
    COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_tickets
FROM tickets;

-- Insert some sample data (optional - remove if not needed)
-- Note: You'll need to update the password hashes with actual hashed passwords
INSERT INTO users (username, email, password_hash, first_name, last_name, is_active) VALUES
('admin', 'admin@ticketpro.com', 'pbkdf2:sha256:600000$placeholder$hash', 'Admin', 'User', TRUE),
('john_doe', 'john@example.com', 'pbkdf2:sha256:600000$placeholder$hash', 'John', 'Doe', TRUE),
('jane_smith', 'jane@example.com', 'pbkdf2:sha256:600000$placeholder$hash', 'Jane', 'Smith', TRUE),
('test_user', 'test@example.com', 'pbkdf2:sha256:600000$placeholder$hash', 'Test', 'User', TRUE);

-- Insert sample tickets
INSERT INTO tickets (title, description, status, priority, user_id) VALUES
('Login Issue', 'Unable to login to the system with correct credentials. Getting error message about invalid username/password.', 'open', 'high', 2),
('Feature Request: PDF Export', 'Add ability to export tickets to PDF format for reporting purposes.', 'open', 'medium', 2),
('Dashboard Bug', 'Dashboard shows incorrect ticket count. Says 5 tickets but I only have 3.', 'in_progress', 'high', 3),
('Account Setup Help', 'Need assistance setting up new user account and understanding the system.', 'closed', 'low', 3),
('Password Reset Not Working', 'Forgot password and reset email is not being received. Checked spam folder.', 'open', 'medium', 2),
('Mobile App Crashes', 'Mobile application crashes when trying to view ticket details.', 'open', 'high', 4),
('Email Notifications', 'Not receiving email notifications when ticket status changes.', 'in_progress', 'medium', 4),
('Performance Issue', 'System is very slow when loading the dashboard with many tickets.', 'open', 'high', 3);

-- Create some useful functions
CREATE OR REPLACE FUNCTION get_user_ticket_count(user_id_param INTEGER)
RETURNS TABLE(total INTEGER, open INTEGER, in_progress INTEGER, closed INTEGER) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total,
        COUNT(*) FILTER (WHERE status = 'open')::INTEGER as open,
        COUNT(*) FILTER (WHERE status = 'in_progress')::INTEGER as in_progress,
        COUNT(*) FILTER (WHERE status = 'closed')::INTEGER as closed
    FROM tickets 
    WHERE user_id = user_id_param;
END;
$$ LANGUAGE plpgsql;

-- Display table information and sample data
\d users
\d tickets

-- Show sample data
SELECT 'Users Table:' as info;
SELECT id, username, email, first_name, last_name, is_active, created_at FROM users;

SELECT 'Tickets Table:' as info;
SELECT id, title, status, priority, user_id, created_at FROM tickets;

SELECT 'Ticket Summary View:' as info;
SELECT * FROM ticket_summary ORDER BY created_at DESC;

SELECT 'Ticket Statistics:' as info;
SELECT * FROM ticket_stats;

-- Test the user ticket count function
SELECT 'User Ticket Counts:' as info;
SELECT 
    u.username,
    (get_user_ticket_count(u.id)).*
FROM users u;
