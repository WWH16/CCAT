// access_keys.js
function validateAndShowModal() {
    const form = document.getElementById('generateForm');
    if (form.checkValidity()) {
        if (hasActiveKey) {
            document.getElementById('confirmation-modal').classList.remove('hidden');
        } else {
            form.submit();
        }
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
function copyKeyCode(code, btn) {
    console.log('copyKeyCode called, code:', code);
    console.log('isSecureContext:', window.isSecureContext);
    console.log('clipboard available:', !!navigator.clipboard);

    const icon = btn.querySelector('.material-symbols-outlined');
    console.log('icon found:', icon);

    const onSuccess = () => {
        console.log('onSuccess called');
        icon.textContent = 'check';
        btn.classList.add('text-green-600');
        setTimeout(() => {
            icon.textContent = 'content_copy';
            btn.classList.remove('text-green-600');
        }, 2000);
    };

    if (navigator.clipboard && window.isSecureContext) {
        console.log('using clipboard API');
        navigator.clipboard.writeText(code).then(onSuccess).catch((err) => {
            console.log('clipboard failed:', err);
            fallbackCopy(code, onSuccess);
        });
    } else {
        console.log('using fallback');
        fallbackCopy(code, onSuccess);
    }
}

function fallbackCopy(text, onSuccess) {
    console.log('fallbackCopy called with:', text);
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.cssText = 'position:fixed;opacity:0;pointer-events:none;';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    console.log('textarea value:', textarea.value);
    try {
        const result = document.execCommand('copy');
        console.log('execCommand result:', result);
        onSuccess();
    } catch (e) {
        console.error('Copy failed:', e);
    }
    document.body.removeChild(textarea);
}

document.querySelectorAll('[id$="-modal"]').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal(modal.id);
    });
});