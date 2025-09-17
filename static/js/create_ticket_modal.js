// Create Ticket Modal Functionality
// This module provides shared functionality for the create ticket modal across all pages

// API helper function (standalone version for modal)
async function apiRequest(url, options = {}) {
    // Ensure URL uses the correct protocol and host
    if (url.startsWith('/')) {
        // Relative URL - ensure it uses the current protocol and host
        url = (window.APP_CONFIG?.API_BASE_URL || (window.location.protocol + '//' + window.location.host)) + url;
        if (window.location.protocol === 'https:' && url.startsWith('http://')) {
            url = url.replace('http://', 'https://');
        }
    } else if (url.startsWith('http://') || url.startsWith('https://')) {
        // Absolute URL - ensure it uses HTTPS if current page is HTTPS
        if (window.location.protocol === 'https:' && url.startsWith('http://')) {
            url = url.replace('http://', 'https://');
        }
    }

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
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

        // Attempt JSON parse only if content-type indicates JSON
        const contentType = response.headers.get('content-type') || '';
        const tryParseJson = async () => {
            if (contentType.includes('application/json')) {
                return await response.json();
            }
            return { error: 'Non-JSON response', status: response.status };
        };

        if (!response.ok) {
            const errorData = await tryParseJson();
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        return await tryParseJson();
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
        // Use admin-specific endpoint that returns only admin users
        const endpoint = '/api/tickets/admin/users';
        try {
            const users = await apiRequest(endpoint);
            const assigneeSelect = document.getElementById('ticketAssignee');

            if (assigneeSelect) {
                assigneeSelect.innerHTML = '<option value="">Unassigned</option>';

                // Support both formats: new endpoint returns username/full_name, fallback if structure differs
                (users || []).forEach(user => {
                    const option = document.createElement('option');
                    option.value = user.id;
                    const name = user.full_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username;
                    option.textContent = name;
                    assigneeSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load assignee options:', error);
            if (typeof showToast === 'function') {
                if (error.message.toLowerCase().includes('network')) {
                    showToast('Network issue loading assignee list. You can still create tickets unassigned.', 'warning');
                } else if (error.message.includes('403')) {
                    showToast('You lack permission to load assignees. Ticket will be unassigned.', 'warning');
                } else if (error.message.includes('401')) {
                    showToast('Session expired. Please log in again to assign.', 'warning');
                } else {
                    showToast('Unable to load assignees. Creating unassigned tickets only.', 'warning');
                }
            }
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
