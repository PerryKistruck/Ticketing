// Create Ticket Modal Functionality
// This module provides shared functionality for the create ticket modal across all pages

// API helper function (standalone version for modal)
async function apiRequest(url, options = {}) {
    // Ensure URL uses the correct protocol and host
    if (url.startsWith('/')) {
        // Relative URL - ensure it uses the current protocol and host
        url = (window.APP_CONFIG?.API_BASE_URL || (window.location.protocol + '//' + window.location.host)) + url;
    } else if (url.startsWith('http://') || url.startsWith('https://')) {
        // Absolute URL - ensure it uses HTTPS if current page is HTTPS
        if (window.location.protocol === 'https:' && url.startsWith('http://')) {
            url = url.replace('http://', 'https://');
        }
    }

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'  // Important for session cookies
    };

    const finalOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    try {
        const response = await fetch(url, finalOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Request failed' }));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        // Re-throw with more context for network errors
        if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
            throw new Error('Network error: Unable to connect to server. Please check your connection.');
        }
        throw error;
    }
}

class CreateTicketModal {
    constructor(options = {}) {
        this.redirectAfterCreate = options.redirectAfterCreate || false;
        this.redirectUrl = options.redirectUrl || '/dashboard';
        this.onTicketCreated = options.onTicketCreated || null;
        this.currentUser = null;
        this.modal = null;
        this.form = null;
        
        this.init();
    }

    init() {
        // Load current user info
        this.loadUserInfo();
        
        // Set up event listeners when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupEventListeners());
        } else {
            this.setupEventListeners();
        }
    }

    loadUserInfo() {
        // Get user info from the template context
        const userElement = document.querySelector('[data-user-info]');
        if (userElement) {
            this.currentUser = JSON.parse(userElement.dataset.userInfo);
        }
    }

    setupEventListeners() {
        this.form = document.getElementById('createTicketForm');
        this.modal = document.getElementById('createTicketModal');
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleCreateTicket(e));
        }

        // Load assignee options for admins
        if (this.currentUser && this.currentUser.is_admin) {
            this.loadAssigneeOptions();
        }
    }

    async handleCreateTicket(e) {
        e.preventDefault();
        
        const formData = {
            title: document.getElementById('ticketTitle').value,
            description: document.getElementById('ticketDescription').value,
            priority: document.getElementById('ticketPriority').value,
            status: document.getElementById('ticketStatus').value
        };

        // Add assignee for admin users
        if (this.currentUser && this.currentUser.is_admin) {
            const assigneeValue = document.getElementById('ticketAssignee').value;
            if (assigneeValue) {
                formData.assigned_to = parseInt(assigneeValue);
            }
        }

        try {
            const newTicket = await apiRequest('/api/tickets', {
                method: 'POST',
                body: JSON.stringify(formData)
            });
            
            // Reset form and close modal
            this.form.reset();
            const modalInstance = bootstrap.Modal.getInstance(this.modal);
            if (modalInstance) {
                modalInstance.hide();
            }
            
            showToast('Ticket created successfully!', 'success');
            
            // Call custom callback if provided
            if (this.onTicketCreated) {
                this.onTicketCreated(newTicket);
            }
            
            // Redirect if specified
            if (this.redirectAfterCreate) {
                setTimeout(() => {
                    window.location.href = this.redirectUrl;
                }, 1500);
            }
            
        } catch (error) {
            showToast('Failed to create ticket: ' + error.message, 'error');
        }
    }

    async loadAssigneeOptions() {
        try {
            const users = await apiRequest('/api/users');
            const assigneeSelect = document.getElementById('ticketAssignee');
            
            if (assigneeSelect) {
                // Clear existing options except "Unassigned"
                assigneeSelect.innerHTML = '<option value="">Unassigned</option>';
                
                // Add admin users
                users.filter(user => user.is_admin).forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    option.textContent = `${user.first_name} ${user.last_name}`;
                    assigneeSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load assignee options:', error);
            
            // Show user-friendly error message
            if (typeof showToast === 'function') {
                if (error.message.includes('Network error')) {
                    showToast('Unable to load assignee options. Network connection issue.', 'warning');
                } else {
                    showToast('Unable to load assignee options. Using default options.', 'warning');
                }
            }
            
            // Ensure at least "Unassigned" option exists
            const assigneeSelect = document.getElementById('ticketAssignee');
            if (assigneeSelect && assigneeSelect.children.length === 0) {
                assigneeSelect.innerHTML = '<option value="">Unassigned</option>';
            }
        }
    }

    // Public method to open the modal programmatically
    show() {
        if (this.modal) {
            const modalInstance = new bootstrap.Modal(this.modal);
            modalInstance.show();
        }
    }

    // Public method to hide the modal programmatically
    hide() {
        if (this.modal) {
            const modalInstance = bootstrap.Modal.getInstance(this.modal);
            if (modalInstance) {
                modalInstance.hide();
            }
        }
    }
}

// Global variable to hold the modal instance
let createTicketModalInstance = null;

// Initialize function that can be called from different pages
function initCreateTicketModal(options = {}) {
    createTicketModalInstance = new CreateTicketModal(options);
    return createTicketModalInstance;
}
