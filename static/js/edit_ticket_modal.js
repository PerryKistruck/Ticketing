// Edit Ticket Modal Functionality
// This module provides shared functionality for the edit ticket modal across all pages


class EditTicketModal {
    constructor(options = {}) {
        this.onTicketUpdated = options.onTicketUpdated || null;
        this.currentUser = null;
        this.modal = null;
        this.form = null;
        this.currentTicket = null;
        this.allTickets = options.allTickets || [];
        
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
        this.form = document.getElementById('editTicketForm');
        this.modal = document.getElementById('editTicketModal');
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleUpdateTicket(e));
        }

        // Load assignee options for admins
        if (this.currentUser && this.currentUser.is_admin) {
            this.loadAssigneeOptions();
        }
    }

    async handleUpdateTicket(e) {
        e.preventDefault();
        
        const id = document.getElementById('editTicketId').value;
        const title = document.getElementById('editTicketTitle').value;
        const description = document.getElementById('editTicketDescription').value;
        const priority = document.getElementById('editTicketPriority').value;
        
        // Prepare the request body
        const updateData = {
            title,
            description,
            priority
        };
        
        // Only include status if the field exists (admin users only)
        const statusField = document.getElementById('editTicketStatus');
        if (statusField) {
            updateData.status = statusField.value;
        }

        // Only include assignee if the field exists (admin users only)
        const assigneeField = document.getElementById('editTicketAssignee');
        if (assigneeField) {
            updateData.assigned_to = assigneeField.value || null;
        }

        try {
            const updatedTicket = await apiRequest(`/api/tickets/${id}`, {
                method: 'PUT',
                body: JSON.stringify(updateData)
            });
            
            // Reset form and close modal
            this.form.reset();
            const modalInstance = bootstrap.Modal.getInstance(this.modal);
            if (modalInstance) {
                modalInstance.hide();
            }
            
            showToast('Ticket updated successfully!', 'success');
            
            // Call custom callback if provided
            if (this.onTicketUpdated) {
                this.onTicketUpdated(updatedTicket);
            }
            
        } catch (error) {
            showToast('Failed to update ticket: ' + error.message, 'error');
        }
    }

    // Open the edit modal with ticket data
    editTicket(ticketId, allTickets = null) {
        // Use provided tickets array or fallback to instance property
        const ticketsArray = allTickets || this.allTickets;
        const ticket = ticketsArray.find(t => t.id === ticketId);
        
        if (!ticket) {
            showToast('Ticket not found', 'error');
            return;
        }

        // Check permissions for regular users (admins can edit any ticket)
        if (!this.currentUser || (!this.currentUser.is_admin && 
            ticket.user_id !== this.currentUser.id && 
            ticket.assigned_to !== this.currentUser.id)) {
            showToast('You can only edit tickets you created or that are assigned to you.', 'error');
            return;
        }

        this.currentTicket = ticket;

        // Populate form fields
        document.getElementById('editTicketId').value = ticket.id;
        document.getElementById('editTicketTitle').value = ticket.title;
        document.getElementById('editTicketDescription').value = ticket.description || '';
        document.getElementById('editTicketPriority').value = ticket.priority;
        
        // Only set status if the field exists (admin users only)
        const statusField = document.getElementById('editTicketStatus');
        if (statusField) {
            statusField.value = ticket.status;
        }

        // Only set assignee if the field exists (admin users only)
        const assigneeField = document.getElementById('editTicketAssignee');
        if (assigneeField) {
            assigneeField.value = ticket.assigned_to || '';
        }

        // Show the modal
        this.show();
    }

    async loadAssigneeOptions() {
        try {
            const users = await apiRequest('/api/tickets/admin/users');
            const assigneeSelect = document.getElementById('editTicketAssignee');
            
            if (assigneeSelect) {
                // Clear existing options except "Unassigned"
                assigneeSelect.innerHTML = '<option value="">Unassigned</option>';
                
                // Add admin users
                users.forEach(user => {
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
            const assigneeSelect = document.getElementById('editTicketAssignee');
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

    // Update the tickets array reference
    updateTicketsArray(ticketsArray) {
        this.allTickets = ticketsArray;
    }
}

// Global variable to hold the modal instance
let editTicketModalInstance = null;

// Initialize function that can be called from different pages
function initEditTicketModal(options = {}) {
    editTicketModalInstance = new EditTicketModal(options);
    return editTicketModalInstance;
}

// Global function for backward compatibility
function editTicket(ticketId, allTickets = null) {
    if (editTicketModalInstance) {
        editTicketModalInstance.editTicket(ticketId, allTickets);
    } else {
        console.error('Edit ticket modal not initialized. Call initEditTicketModal() first.');
    }
}
