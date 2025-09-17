// Dashboard functionality

let allTickets = [];
let filteredTickets = [];
let currentUser = null;

document.addEventListener('DOMContentLoaded', function() {
    loadUserInfo();
    loadTickets();
    setupEventListeners();
    
    // Initialize create ticket modal with dashboard-specific options
    initCreateTicketModal({
        redirectAfterCreate: false,
        onTicketCreated: (newTicket) => {
            // Add the new ticket to the dashboard
            allTickets.unshift(newTicket);
            applyFilters();
            updateStats();
        }
    });
});

function loadUserInfo() {
    // Get user info from the template context
    const userElement = document.querySelector('[data-user-info]');
    if (userElement) {
        currentUser = JSON.parse(userElement.dataset.userInfo);
    }
}

function setupEventListeners() {
    // Filters
    const statusFilter = document.getElementById('statusFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    
    if (statusFilter) statusFilter.addEventListener('change', applyFilters);
    if (priorityFilter) priorityFilter.addEventListener('change', applyFilters);

    // Initialize edit ticket modal
    initEditTicketModal({
        onTicketUpdated: (updatedTicket) => {
            // Update the ticket in our local arrays
            const ticketIndex = allTickets.findIndex(t => t.id === updatedTicket.id);
            if (ticketIndex !== -1) {
                allTickets[ticketIndex] = updatedTicket;
            }
            
            // Reapply filters and update display
            applyFilters();
            updateStats();
        },
        allTickets: allTickets
    });
}

async function loadTickets() {
    try {
        showLoading(true);
        const tickets = await apiRequest('/api/tickets');
        
        // Regular dashboard always shows personal tickets only
        // No admin filtering needed here - backend handles it
        allTickets = tickets;
        filteredTickets = allTickets;
        
        // Update the edit modal's tickets array reference
        if (editTicketModalInstance) {
            editTicketModalInstance.updateTicketsArray(allTickets);
        }
        
        updateDashboard();
        showLoading(false);
    } catch (error) {
        // More detailed error message
        let errorMessage = 'Failed to load tickets';
        if (error.message.includes('401')) {
            errorMessage = 'Authentication required. Please log in again.';
        } else if (error.message.includes('403')) {
            errorMessage = 'You do not have permission to view tickets.';
        } else if (error.message.includes('500')) {
            errorMessage = 'Server error. Please try again later.';
        } else if (error.message.includes('Failed to fetch')) {
            errorMessage = 'Network error. Please check your connection and try again.';
        }
        
        showToast(errorMessage, 'error');
        showLoading(false);
        
        // Show empty state
        allTickets = [];
        filteredTickets = [];
        updateDashboard();
    }
}

function updateDashboard() {
    updateStats();
    updateTicketsTable();
}

function updateStats() {
    // Use allTickets (which are already filtered for non-admin users)
    const total = allTickets.length;
    const open = allTickets.filter(t => t.status === 'open').length;
    const inProgress = allTickets.filter(t => t.status === 'in_progress').length;
    const closed = allTickets.filter(t => t.status === 'closed').length;

    document.getElementById('totalTickets').textContent = total;
    document.getElementById('openTickets').textContent = open;
    document.getElementById('inProgressTickets').textContent = inProgress;
    document.getElementById('closedTickets').textContent = closed;
}

function updateTicketsTable() {
    const tbody = document.getElementById('ticketsTableBody');
    const ticketsTable = document.getElementById('ticketsTable');
    const noTickets = document.getElementById('noTickets');

    if (filteredTickets.length === 0) {
        ticketsTable.style.display = 'none';
        noTickets.style.display = 'block';
        return;
    }

    ticketsTable.style.display = 'block';
    noTickets.style.display = 'none';

    tbody.innerHTML = filteredTickets.map(ticket => {
        // Check if user can edit this ticket (created by them or assigned to them)
        const canEdit = currentUser && (ticket.user_id === currentUser.id || ticket.assigned_to === currentUser.id);
        
        return `
        <tr class="fade-in">
            <td>
                #${ticket.id}
                ${currentUser && ticket.user_id === currentUser.id ? 
                    '<br><small class="badge bg-success">Created by me</small>' : ''}
                ${currentUser && ticket.assigned_to === currentUser.id ? 
                    '<br><small class="badge bg-info">Assigned to me</small>' : ''}
            </td>
            <td>
                <strong>${escapeHtml(ticket.title)}</strong>
                ${ticket.description ? `<br><small class="text-muted">${escapeHtml(ticket.description.substring(0, 50))}${ticket.description.length > 50 ? '...' : ''}</small>` : ''}
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
                ${ticket.assignee_name ? `
                    <span class="text-primary">
                        <i class="fas fa-user me-1"></i>${escapeHtml(ticket.assignee_name)}
                    </span>
                ` : '<span class="text-muted"><i class="fas fa-user-slash me-1"></i>Unassigned</span>'}
            </td>
            <td>${formatDate(ticket.created_at)}</td>
            <td>
                ${canEdit ? `
                    <button class="btn btn-outline-primary btn-sm" onclick="editTicket(${ticket.id})" title="Edit Ticket">
                        <i class="fas fa-edit"></i>
                    </button>
                ` : '<span class="text-muted"><i class="fas fa-lock"></i></span>'}
            </td>
        </tr>`
    }).join('');
}

function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value;
    const priorityFilter = document.getElementById('priorityFilter').value;

    filteredTickets = allTickets.filter(ticket => {
        const statusMatch = !statusFilter || ticket.status === statusFilter;
        const priorityMatch = !priorityFilter || ticket.priority === priorityFilter;
        return statusMatch && priorityMatch;
    });

    updateTicketsTable();
}


// Show toast notifications
function showToast(message, type = 'info') {
    // Simple implementation - you can replace with a proper toast library
    console.log(`${type.toUpperCase()}: ${message}`);
    
    // For now, use alerts for important messages
    if (type === 'error') {
        alert('Error: ' + message);
    } else if (type === 'success' && message.includes('successfully')) {
        // Only show success alerts for important actions
        alert(message);
    }
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

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

function showLoading(show) {
    const spinner = document.getElementById('loadingSpinner');
    const table = document.getElementById('ticketsTable');
    const noTickets = document.getElementById('noTickets');

    if (show) {
        spinner.style.display = 'block';
        table.style.display = 'none';
        noTickets.style.display = 'none';
    } else {
        spinner.style.display = 'none';
    }
}