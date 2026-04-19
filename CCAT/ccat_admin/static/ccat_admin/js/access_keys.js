// access_keys.js
function validateAndShowModal() {
    const form = document.getElementById('generateForm');
    if (form.checkValidity()) {
        document.getElementById('confirmation-modal').classList.remove('hidden');
    } else {
        form.reportValidity();
    }
}

function showRevokeModal(sessionName, url) {
    document.getElementById('revoke-session-name').innerText = sessionName;
    document.getElementById('revokeForm').action = url;
    document.getElementById('revoke-modal').classList.remove('hidden');
}

function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}

// Set minimum date to now
const expiryInput = document.getElementById('expiry_date');
if (expiryInput) {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    expiryInput.min = now.toISOString().slice(0, 16);
}