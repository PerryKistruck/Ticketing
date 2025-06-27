// Dashboard functionality

let allTickets = [];
let filteredTickets = [];

document.addEventListener('DOMContentLoaded', function() {
    loadTickets();
    setupEventListeners();
});

function setupEventListeners() {
    // Create ticket form
    document.getElementById('createTicketForm').addEventListener('submit', handleCreateTicket);
    
    // Edit ticket form
    document.getElementById('editTicketForm').addEventListener('submit', handleEditTicket);
    
    // Filters
    document.getElementById('statusFilter').addEventListener('change', applyFilters);
    document.getElementById('priorityFilter').addEventListener('change', applyFilters);
}

async function loadTickets() {
    try {
        showLoading(true);
        const tickets = await apiRequest('/api/tickets');
        allTickets = tickets;
        filteredTickets = tickets;
        updateDashboard();
        showLoading(false);
    } catch (error) {
        showToast('Failed to load tickets: ' + error.message, 'error');
        showLoading(false);
    }
}

function updateDashboard() {
    updateStats();
    updateTicketsTable();
}

function updateStats() {
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

    tbody.innerHTML = filteredTickets.map(ticket => `
        <tr class="fade-in">
            <td>#${ticket.id}</td>
            <td>
                <strong>${ticket.title}</strong>
                ${ticket.description ? `<br><small class="text-muted">${ticket.description.substring(0, 50)}${ticket.description.length > 50 ? '...' : ''}</small>` : ''}
            </td>
            <td>
                <span class="badge badge-status status-${ticket.status}">
                    ${capitalize(ticket.status.replace('_', ' '))}
                </span>
            </td>
            <td>
                <span class="badge priority-${ticket.priority}">
                    ${capitalize(ticket.priority)}
                </span>
            </td>
            <td>${formatDate(ticket.created_at)}</td>
            <td>
                <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-primary" onclick="editTicket(${ticket.id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-outline-danger" onclick="deleteTicket(${ticket.id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
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

async function handleCreateTicket(e) {
    e.preventDefault();
    
    const formData = {
        title: document.getElementById('ticketTitle').value,
        description: document.getElementById('ticketDescription').value,
        priority: document.getElementById('ticketPriority').value,
        status: document.getElementById('ticketStatus').value
    };

    try {
        const newTicket = await apiRequest('/api/tickets', {
            method: 'POST',
            body: JSON.stringify(formData)
        });

        allTickets.unshift(newTicket);
        applyFilters();
        updateStats();
        
        // Reset form and close modal
        document.getElementById('createTicketForm').reset();
        bootstrap.Modal.getInstance(document.getElementById('createTicketModal')).hide();
        
        showToast('Ticket created successfully!', 'success');
    } catch (error) {
        showToast('Failed to create ticket: ' + error.message, 'error');
    }
}

function editTicket(ticketId) {
    const ticket = allTickets.find(t => t.id === ticketId);
    if (!ticket) return;

    document.getElementById('editTicketId').value = ticket.id;
    document.getElementById('editTicketTitle').value = ticket.title;
    document.getElementById('editTicketDescription').value = ticket.description || '';
    document.getElementById('editTicketPriority').value = ticket.priority;
    document.getElementById('editTicketStatus').value = ticket.status;

    new bootstrap.Modal(document.getElementById('editTicketModal')).show();
}

async function handleEditTicket(e) {
    e.preventDefault();
    
    const ticketId = document.getElementById('editTicketId').value;
    const formData = {
        title: document.getElementById('editTicketTitle').value,
        description: document.getElementById('editTicketDescription').value,
        priority: document.getElementById('editTicketPriority').value,
        status: document.getElementById('editTicketStatus').value
    };

    try {
        const updatedTicket = await apiRequest(`/api/tickets/${ticketId}`, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });

        // Update ticket in local array
        const index = allTickets.findIndex(t => t.id == ticketId);
        if (index !== -1) {
            allTickets[index] = updatedTicket;
            applyFilters();
            updateStats();
        }
        
        bootstrap.Modal.getInstance(document.getElementById('editTicketModal')).hide();
        showToast('Ticket updated successfully!', 'success');
    } catch (error) {
        showToast('Failed to update ticket: ' + error.message, 'error');
    }
}

async function deleteTicket(ticketId) {
    if (!confirm('Are you sure you want to delete this ticket?')) return;

    try {
        await apiRequest(`/api/tickets/${ticketId}`, {
            method: 'DELETE'
        });

        allTickets = allTickets.filter(t => t.id !== ticketId);
        applyFilters();
        updateStats();
        
        showToast('Ticket deleted successfully!', 'success');
    } catch (error) {
        showToast('Failed to delete ticket: ' + error.message, 'error');
    }
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