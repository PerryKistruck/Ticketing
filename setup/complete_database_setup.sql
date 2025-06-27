-- TicketPro Complete Database Setup Script for PostgreSQL
-- This script creates all necessary tables, indexes, views, and functions for the ticketing system
-- Includes both basic functionality and admin features

-- Create database (run this separately if needed)
-- CREATE DATABASE ticketpro;
-- \c ticketpro;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop views if they exist
DROP VIEW IF EXISTS ticket_summary CASCADE;
DROP VIEW IF EXISTS ticket_stats CASCADE;
DROP VIEW IF EXISTS admin_ticket_stats CASCADE;

-- Drop functions if they exist
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS get_user_ticket_count(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS get_admin_tickets(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS get_unassigned_tickets() CASCADE;

-- ============================================================================
-- TABLE CREATION
-- ============================================================================

-- Create Users table with admin support
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Add constraints
    CONSTRAINT chk_username_length CHECK (LENGTH(username) >= 3),
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT chk_name_length CHECK (LENGTH(first_name) >= 1 AND LENGTH(last_name) >= 1)
);

-- Create Tickets table with admin assignment support
CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'medium',
    user_id INTEGER NOT NULL,
    assigned_to INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_tickets_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_tickets_assigned_to FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Check constraints for data integrity
    CONSTRAINT chk_status CHECK (status IN ('open', 'in_progress', 'closed', 'cancelled')),
    CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    CONSTRAINT chk_title_length CHECK (LENGTH(title) >= 1)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- User table indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_users_is_admin ON users(is_admin);

-- Ticket table indexes
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_tickets_updated_at ON tickets(updated_at);

-- Composite indexes for common queries
CREATE INDEX idx_tickets_user_status ON tickets(user_id, status);
CREATE INDEX idx_tickets_user_priority ON tickets(user_id, priority);
CREATE INDEX idx_tickets_status_priority ON tickets(status, priority);
CREATE INDEX idx_tickets_user_created ON tickets(user_id, created_at DESC);
CREATE INDEX idx_tickets_assigned_status ON tickets(assigned_to, status);

-- ============================================================================
-- TRIGGERS AND FUNCTIONS
-- ============================================================================

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

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to get user ticket counts
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

-- Function to get tickets assigned to a specific admin
CREATE OR REPLACE FUNCTION get_admin_tickets(admin_id_param INTEGER)
RETURNS TABLE(
    ticket_id INTEGER,
    title VARCHAR(200),
    description TEXT,
    status VARCHAR(20),
    priority VARCHAR(20),
    requester_name TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.title,
        t.description,
        t.status,
        t.priority,
        CONCAT(u.first_name, ' ', u.last_name) as requester_name,
        t.created_at,
        t.updated_at
    FROM tickets t
    JOIN users u ON t.user_id = u.id
    WHERE t.assigned_to = admin_id_param
    ORDER BY t.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get unassigned tickets
CREATE OR REPLACE FUNCTION get_unassigned_tickets()
RETURNS TABLE(
    ticket_id INTEGER,
    title VARCHAR(200),
    description TEXT,
    status VARCHAR(20),
    priority VARCHAR(20),
    requester_name TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.title,
        t.description,
        t.status,
        t.priority,
        CONCAT(u.first_name, ' ', u.last_name) as requester_name,
        t.created_at,
        t.updated_at
    FROM tickets t
    JOIN users u ON t.user_id = u.id
    WHERE t.assigned_to IS NULL
    ORDER BY 
        CASE t.priority 
            WHEN 'urgent' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END,
        t.created_at ASC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS FOR REPORTING AND QUERIES
-- ============================================================================

-- Comprehensive ticket summary view with assignee information
CREATE VIEW ticket_summary AS
SELECT 
    t.id,
    t.title,
    t.description,
    t.status,
    t.priority,
    CONCAT(u.first_name, ' ', u.last_name) as requester_name,
    u.email as requester_email,
    CASE 
        WHEN t.assigned_to IS NOT NULL 
        THEN CONCAT(a.first_name, ' ', a.last_name) 
        ELSE 'Unassigned' 
    END as assignee_name,
    a.email as assignee_email,
    t.created_at,
    t.updated_at,
    -- Time elapsed since creation
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.created_at))/3600 as hours_since_creation,
    -- Days since last update
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - t.updated_at))/86400 as days_since_update
FROM tickets t
JOIN users u ON t.user_id = u.id
LEFT JOIN users a ON t.assigned_to = a.id
ORDER BY t.created_at DESC;

-- Basic ticket statistics view
CREATE VIEW ticket_stats AS
SELECT 
    COUNT(*) as total_tickets,
    COUNT(*) FILTER (WHERE status = 'open') as open_tickets,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tickets,
    COUNT(*) FILTER (WHERE status = 'closed') as closed_tickets,
    COUNT(*) FILTER (WHERE priority = 'high') as high_priority_tickets,
    COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_tickets
FROM tickets;

-- Admin dashboard statistics view
CREATE VIEW admin_ticket_stats AS
SELECT 
    COUNT(*) as total_tickets,
    COUNT(*) FILTER (WHERE status = 'open') as open_tickets,
    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tickets,
    COUNT(*) FILTER (WHERE status = 'closed') as closed_tickets,
    COUNT(*) FILTER (WHERE assigned_to IS NULL) as unassigned_tickets,
    COUNT(*) FILTER (WHERE priority = 'high') as high_priority_tickets,
    COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_tickets,
    COUNT(DISTINCT user_id) as unique_requesters,
    COUNT(DISTINCT assigned_to) as unique_assignees
FROM tickets;

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- Insert sample users (including admin user)
-- Note: You'll need to update the password hashes with actual hashed passwords
INSERT INTO users (username, email, password_hash, first_name, last_name, is_admin, is_active) VALUES
('admin', 'admin@ticketpro.com', 'pbkdf2:sha256:600000$placeholder$hash', 'System', 'Administrator', TRUE, TRUE),
('john_doe', 'john@example.com', 'pbkdf2:sha256:600000$placeholder$hash', 'John', 'Doe', FALSE, TRUE),
('jane_smith', 'jane@example.com', 'pbkdf2:sha256:600000$placeholder$hash', 'Jane', 'Smith', FALSE, TRUE),
('test_user', 'test@example.com', 'pbkdf2:sha256:600000$placeholder$hash', 'Test', 'User', FALSE, TRUE),
('support_admin', 'support@ticketpro.com', 'pbkdf2:sha256:600000$placeholder$hash', 'Support', 'Admin', TRUE, TRUE);

-- Insert sample tickets with some assigned to admins
INSERT INTO tickets (title, description, status, priority, user_id, assigned_to) VALUES
('Login Issue', 'Unable to login to the system with correct credentials. Getting error message about invalid username/password.', 'in_progress', 'high', 2, 1),
('Feature Request: PDF Export', 'Add ability to export tickets to PDF format for reporting purposes.', 'open', 'medium', 2, NULL),
('Dashboard Bug', 'Dashboard shows incorrect ticket count. Says 5 tickets but I only have 3.', 'in_progress', 'high', 3, 5),
('Account Setup Help', 'Need assistance setting up new user account and understanding the system.', 'closed', 'low', 3, 1),
('Password Reset Not Working', 'Forgot password and reset email is not being received. Checked spam folder.', 'open', 'medium', 2, NULL),
('Mobile App Crashes', 'Mobile application crashes when trying to view ticket details.', 'open', 'high', 4, NULL),
('Email Notifications', 'Not receiving email notifications when ticket status changes.', 'in_progress', 'medium', 4, 5),
('Performance Issue', 'System is very slow when loading the dashboard with many tickets.', 'open', 'high', 3, NULL),
('Database Connection Error', 'Getting intermittent database connection errors during peak hours.', 'open', 'urgent', 2, 1),
('UI Improvement Request', 'Suggestion to improve the user interface for better accessibility.', 'open', 'low', 4, NULL);

-- ============================================================================
-- VERIFICATION AND DISPLAY
-- ============================================================================

-- Display success message
SELECT 'TicketPro Database Setup Completed Successfully!' as message;

-- Display table information
\d users
\d tickets

-- Show sample data
SELECT 'Users Table:' as info;
SELECT id, username, email, first_name, last_name, is_admin, is_active, created_at FROM users ORDER BY id;

SELECT 'Tickets Table:' as info;
SELECT id, title, status, priority, user_id, assigned_to, created_at FROM tickets ORDER BY id;

-- Show comprehensive ticket summary
SELECT 'Ticket Summary View:' as info;
SELECT id, title, status, priority, requester_name, assignee_name, created_at 
FROM ticket_summary 
ORDER BY created_at DESC;

-- Show statistics
SELECT 'Basic Ticket Statistics:' as info;
SELECT * FROM ticket_stats;

SELECT 'Admin Dashboard Statistics:' as info;
SELECT * FROM admin_ticket_stats;

-- Show admin users
SELECT 'Admin Users:' as info;
SELECT id, username, email, first_name, last_name 
FROM users 
WHERE is_admin = TRUE;

-- Show unassigned tickets
SELECT 'Unassigned Tickets:' as info;
SELECT ticket_id, title, status, priority, requester_name 
FROM get_unassigned_tickets() 
LIMIT 10;

-- Test the user ticket count function
SELECT 'User Ticket Counts:' as info;
SELECT 
    u.username,
    (get_user_ticket_count(u.id)).*
FROM users u
ORDER BY u.id;

-- Show tickets assigned to admins
SELECT 'Admin Assigned Tickets:' as info;
SELECT 
    u.username as admin_username,
    COUNT(t.id) as assigned_tickets
FROM users u
LEFT JOIN tickets t ON u.id = t.assigned_to
WHERE u.is_admin = TRUE
GROUP BY u.id, u.username
ORDER BY u.id;
