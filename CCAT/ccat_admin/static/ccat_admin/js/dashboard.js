// dashboard.js
function copyKeyCode(code, btn) {
    const icon = btn.querySelector('.material-symbols-outlined');
    const onSuccess = () => {
        icon.textContent = 'check';
        btn.classList.add('text-green-600');
        setTimeout(() => {
            icon.textContent = 'content_copy';
            btn.classList.remove('text-green-600');
        }, 2000);
    };
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(code).then(onSuccess).catch(() => fallbackCopy(code, onSuccess));
    } else {
        fallbackCopy(code, onSuccess);
    }
}

function fallbackCopy(text, onSuccess) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.cssText = 'position:fixed;opacity:0;pointer-events:none;';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    try {
        document.execCommand('copy');
        onSuccess();
    } catch (e) {
        console.error('Copy failed:', e);
    }
    document.body.removeChild(textarea);
}