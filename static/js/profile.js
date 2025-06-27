// Profile page functionality

document.addEventListener('DOMContentLoaded', function() {
    setupProfileForm();
});

function setupProfileForm() {
    document.getElementById('profileForm').addEventListener('submit', handleProfileUpdate);
}

async function handleProfileUpdate(e) {
    e.preventDefault();
    
    const userId = getCurrentUserId(); // You'll need to implement this
    const formData = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        username: document.getElementById('username').value,
        email: document.getElementById('email').value
    };

    const newPassword = document.getElementById('newPassword').value;
    if (newPassword) {
        formData.password = newPassword;
    }

    try {
        await apiRequest(`/api/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(formData)
        });

        showToast('Profile updated successfully!', 'success');
        
        // Clear password field
        document.getElementById('newPassword').value = '';
    } catch (error) {
        showToast('Failed to update profile: ' + error.message, 'error');
    }
}

// This function should get the current user ID from the session
// You might need to pass this from the template or make an API call
function getCurrentUserId() {
    // Implementation depends on how you want to handle this
    // For now, you could add a hidden input in the template with the user ID
    return document.querySelector('[data-user-id]')?.dataset.userId;
}