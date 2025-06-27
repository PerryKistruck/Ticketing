// Admin Dashboard JavaScript
let tickets = [];
let adminUsers = [];
let filteredTickets = [];

document.addEventListener('DOMContentLoaded', function() {
    loadAdminUsers();
    loadTickets();
    setupEventListeners();
    
    // Initialize create ticket modal with admin dashboard-specific options
    initCreateTicketModal({
        redirectAfterCreate: false,
        onTicketCreated: (newTicket) => {
            // Add the new ticket to the admin dashboard
            tickets.unshift(newTicket);
            updateStats();
            filterTickets();
        }
    });
});

function setupEventListeners() {
    // Edit ticket form
    document.getElementById('editTicketForm').addEventListener('submit', function(e) {
        e.preventDefault();
        updateTicket();
    });

    // Assign ticket form
    document.getElementById('assignTicketForm').addEventListener('submit', function(e) {
        e.preventDefault();
        assignTicket();
    });
}

async function loadAdminUsers() {
    try {
        const response = await fetch('/api/tickets/admin/users');
        if (response.ok) {
            adminUsers = await response.json();
            populateAssigneeDropdowns();
        }
    } catch (error) {
        console.error('Error loading admin users:', error);
    }
}

function populateAssigneeDropdowns() {
    const dropdowns = ['ticketAssignee', 'editTicketAssignee', 'assignTicketTo', 'assigneeFilter'];
    
    dropdowns.forEach(dropdownId => {
        const dropdown = document.getElementById(dropdownId);
        if (!dropdown) return;
        
        // Clear existing options (except the first one for most dropdowns)
        const keepFirst = dropdownId !== 'assignTicketTo';
        if (keepFirst) {
            dropdown.innerHTML = dropdown.firstElementChild.outerHTML;
        } else {
            dropdown.innerHTML = '<option value="">Select Admin</option>';
        }
        
        // Add admin users
        adminUsers.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.full_name;
            dropdown.appendChild(option);
        });
    });
}

async function loadTickets() {
    try {
        const response = await fetch('/api/tickets/admin/all');
        if (response.ok) {
            tickets = await response.json();
            filteredTickets = [...tickets];
            displayTickets();
            updateStats();
        } else {
            showError('Failed to load tickets');
        }
    } catch (error) {
        console.error('Error loading tickets:', error);
        showError('Error loading tickets');
    }
}

function displayTickets() {
    const tbody = document.getElementById('ticketsTableBody');
    const noTickets = document.getElementById('noTickets');
    const ticketsTable = document.getElementById('ticketsTable');

    if (filteredTickets.length === 0) {
        ticketsTable.style.display = 'none';
        noTickets.style.display = 'block';
        return;
    }

    ticketsTable.style.display = 'block';
    noTickets.style.display = 'none';

    tbody.innerHTML = filteredTickets.map(ticket => `
        <tr>
            <td><span class="badge bg-secondary">#${ticket.id}</span></td>
            <td>
                <strong>${escapeHtml(ticket.title)}</strong>
                ${ticket.description ? `<br><small class="text-muted">${escapeHtml(ticket.description.substring(0, 50))}${ticket.description.length > 50 ? '...' : ''}</small>` : ''}
            </td>
            <td>
                <span class="text-primary">
                    <i class="fas fa-user me-1"></i>${escapeHtml(ticket.user_name)}
                </span>
            </td>
            <td>
                <span class="badge badge-status status-${ticket.status}">
                    ${capitalize(ticket.status.replace('_', ' '))}
                </span>
            </td>
            <td>
                <span class="badge priority-${ticket.priority} ${(ticket.priority === 'high' || ticket.priority === 'urgent') ? 'priority-urgent' : ''}">
                    ${(ticket.priority === 'high' || ticket.priority === 'urgent') ? 'URGENT' : capitalize(ticket.priority)}
                </span>
            </td>
            <td>
                ${ticket.assignee_name ? 
                    `<span class="text-success"><i class="fas fa-user-check me-1"></i>${escapeHtml(ticket.assignee_name)}</span>` : 
                    '<span class="text-warning"><i class="fas fa-user-slash me-1"></i>Unassigned</span>'
                }
            </td>
            <td><small class="text-muted">${formatDate(ticket.created_at)}</small></td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editTicket(${ticket.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-success" onclick="showAssignModal(${ticket.id})" title="Assign">
                        <i class="fas fa-user-check"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteTicket(${ticket.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function updateStats() {
    const total = tickets.length;
    const unassigned = tickets.filter(t => !t.assigned_to).length;
    const inProgress = tickets.filter(t => t.status === 'in_progress').length;
    const closed = tickets.filter(t => t.status === 'closed').length;

    document.getElementById('totalTickets').textContent = total;
    document.getElementById('unassignedTickets').textContent = unassigned;
    document.getElementById('inProgressTickets').textContent = inProgress;
    document.getElementById('closedTickets').textContent = closed;
}

function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value;
    const priorityFilter = document.getElementById('priorityFilter').value;
    const assigneeFilter = document.getElementById('assigneeFilter').value;

    filteredTickets = tickets.filter(ticket => {
        const statusMatch = !statusFilter || ticket.status === statusFilter;
        const priorityMatch = !priorityFilter || ticket.priority === priorityFilter;
        
        let assigneeMatch = true;
        if (assigneeFilter) {
            if (assigneeFilter === 'unassigned') {
                assigneeMatch = !ticket.assigned_to;
            } else {
                assigneeMatch = ticket.assigned_to && ticket.assigned_to.toString() === assigneeFilter;
            }
        }

        return statusMatch && priorityMatch && assigneeMatch;
    });

    displayTickets();
}

function clearFilters() {
    document.getElementById('statusFilter').value = '';
    document.getElementById('priorityFilter').value = '';
    document.getElementById('assigneeFilter').value = '';
    filteredTickets = [...tickets];
    displayTickets();
}

function editTicket(ticketId) {
    const ticket = tickets.find(t => t.id === ticketId);
    if (!ticket) return;

    document.getElementById('editTicketId').value = ticket.id;
    document.getElementById('editTicketTitle').value = ticket.title;
    document.getElementById('editTicketDescription').value = ticket.description || '';
    document.getElementById('editTicketPriority').value = ticket.priority;
    document.getElementById('editTicketStatus').value = ticket.status;
    document.getElementById('editTicketAssignee').value = ticket.assigned_to || '';

    const modal = new bootstrap.Modal(document.getElementById('editTicketModal'));
    modal.show();
}

async function updateTicket() {
    const id = document.getElementById('editTicketId').value;
    const title = document.getElementById('editTicketTitle').value;
    const description = document.getElementById('editTicketDescription').value;
    const priority = document.getElementById('editTicketPriority').value;
    const status = document.getElementById('editTicketStatus').value;
    const assignedTo = document.getElementById('editTicketAssignee').value;

    try {
        const response = await fetch(`/api/tickets/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                description,
                priority,
                status,
                assigned_to: assignedTo || null
            })
        });

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('editTicketModal'));
            modal.hide();
            loadTickets();
            showSuccess('Ticket updated successfully');
        } else {
            const error = await response.json();
            showError(error.error || 'Failed to update ticket');
        }
    } catch (error) {
        console.error('Error updating ticket:', error);
        showError('Error updating ticket');
    }
}

function showAssignModal(ticketId) {
    document.getElementById('assignTicketId').value = ticketId;
    document.getElementById('assignTicketTo').value = '';
    
    const modal = new bootstrap.Modal(document.getElementById('assignTicketModal'));
    modal.show();
}

async function assignTicket() {
    const ticketId = document.getElementById('assignTicketId').value;
    const assignedTo = document.getElementById('assignTicketTo').value;

    try {
        const response = await fetch(`/api/tickets/admin/assign/${ticketId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                assigned_to: assignedTo
            })
        });

        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('assignTicketModal'));
            modal.hide();
            loadTickets();
            showSuccess('Ticket assigned successfully');
        } else {
            const error = await response.json();
            showError(error.error || 'Failed to assign ticket');
        }
    } catch (error) {
        console.error('Error assigning ticket:', error);
        showError('Error assigning ticket');
    }
}

async function deleteTicket(ticketId) {
    if (!confirm('Are you sure you want to delete this ticket? This action cannot be undone.')) {
        return;
    }

    try {
        const response = await fetch(`/api/tickets/${ticketId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            loadTickets();
            showSuccess('Ticket deleted successfully');
        } else {
            const error = await response.json();
            showError(error.error || 'Failed to delete ticket');
        }
    } catch (error) {
        console.error('Error deleting ticket:', error);
        showError('Error deleting ticket');
    }
}

function refreshTickets() {
    loadTickets();
    showSuccess('Tickets refreshed');
}

// Utility functions
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

function showSuccess(message) {
    // You can implement toast notifications here
    console.log('Success:', message);
    // Simple alert for now
    if (message !== 'Tickets refreshed') {
        alert(message);
    }
}

function showError(message) {
    // You can implement toast notifications here
    console.error('Error:', message);
    alert('Error: ' + message);
}
