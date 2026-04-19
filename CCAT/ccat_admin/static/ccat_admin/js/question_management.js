    function getCSRFToken() {
        const cookieValue = document.cookie.match('(^|; )csrftoken=([^;]*)')?.pop();
        return cookieValue;
    }
    function toggleModal(modalId, show) {
        const modal = document.getElementById(modalId);
        if (show) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        } else {
            modal.classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
    }

    // ── Add modal layouts
function switchLayout(selectedType) {
    document.getElementById('mcqLayout').classList.toggle('hidden', selectedType !== 'MCQ');
    document.getElementById('tfLayout').classList.toggle('hidden', selectedType === 'MCQ');
    document.getElementById('addAnswerError').classList.add('hidden');
    document.getElementById('mcqLayout').querySelectorAll('.flex.items-center').forEach(r => r.classList.remove('bg-error/10', 'ring-1', 'ring-error', 'rounded-xl'));
    document.getElementById('tfLayout').querySelectorAll('label').forEach(l => l.classList.remove('bg-error/10', 'ring-1', 'ring-error'));
}


    // ── Edit modal layouts
function switchEditLayout(selectedType) {
    document.getElementById('editMcqLayout').classList.toggle('hidden', selectedType !== 'MCQ');
    document.getElementById('editTfLayout').classList.toggle('hidden', selectedType === 'MCQ');
    document.getElementById('editAnswerError').classList.add('hidden');
    document.getElementById('editMcqLayout').querySelectorAll('.flex.items-center').forEach(r => r.classList.remove('bg-error/10', 'ring-1', 'ring-error', 'rounded-xl'));
    document.getElementById('editTfLayout').querySelectorAll('label').forEach(l => l.classList.remove('bg-error/10', 'ring-1', 'ring-error'));
}

    // ── Open Edit Modal
    function openEditModal(questionId, questionText, questionType, categoryName, btn) {
        document.getElementById('editForm').action = btn.dataset.editUrl;

        // Populate text
        document.getElementById('editText').value = questionText;

        // Set type & toggle layout
        const typeSelect = document.getElementById('editType');
        typeSelect.value = questionType;
        switchEditLayout(questionType);

        // Set category by matching data-name
        const catSelect = document.getElementById('editCategory');
        for (let opt of catSelect.options) {
            if (opt.dataset.name === categoryName) {
                catSelect.value = opt.value;
                break;
            }
        }

        // Pre-fill choices from the row's data-options attribute
        const row = btn.closest('tr');
        const options = JSON.parse(row.dataset.options || '[]');
        const letters = ['A', 'B', 'C', 'D'];

        // Clear all first
        letters.forEach(l => {
            const inp = document.getElementById(`editOption${l}`);
            const radio = document.getElementById(`editCorrect${l}`);
            if (inp) inp.value = '';
            if (radio) radio.checked = false;
        });

        if (questionType === 'MCQ') {
            // Fill MCQ choices
            options.forEach((opt, i) => {
                const letter = letters[i];
                if (!letter) return;
                const inp   = document.getElementById(`editOption${letter}`);
                const radio = document.getElementById(`editCorrect${letter}`);
                if (inp) inp.value = opt.text;
                if (radio && opt.correct) radio.checked = true;
            });
        } else {
            // Pre-check the correct T/F radio
            const correctLabel = options.find(o => o.correct)?.text; // 'True' or 'False'
            document.querySelectorAll('#editTfLayout input[type="radio"]').forEach(radio => {
                radio.checked = (radio.value === correctLabel);
            });
        }

        toggleModal('editModal', true);
    }

    // ── Open Delete Modal
    function openDeleteModal(btn, questionText) {
        document.getElementById('deleteForm').action = btn.dataset.deleteUrl;
        document.getElementById('deleteQuestionPreview').textContent = questionText;
        toggleModal('deleteModal', true);
    }

    // ── Search & Category Filter
    function filterQuestions() {
        const searchTerm = document.getElementById('searchInput').value.toLowerCase();
        const selectedCategory = document.getElementById('categoryFilter').value;
        const rows = document.querySelectorAll('.question-row');

        rows.forEach(row => {
            const qId       = row.querySelector('td:nth-child(1)').textContent.toLowerCase();
            const qText     = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const qAnswer   = row.querySelector('td:nth-child(5)').textContent.toLowerCase();
            const rowCat    = row.getAttribute('data-category');

            const matchesSearch   = qId.includes(searchTerm) || qText.includes(searchTerm) || qAnswer.includes(searchTerm);
            const matchesCategory = (selectedCategory === 'all' || rowCat === selectedCategory);

            row.style.display = (matchesSearch && matchesCategory) ? '' : 'none';
        });
    }
function validateAnswer(form) {
    const type = form.querySelector('[name="question_type"]').value;
    const errorId = form.id === 'editForm' ? 'editAnswerError' : 'addAnswerError';
    const errorEl = document.getElementById(errorId);

    // Clear previous highlights
    const mcqId = form.id === 'editForm' ? 'editMcqLayout' : 'mcqLayout';
    const tfId  = form.id === 'editForm' ? 'editTfLayout'  : 'tfLayout';
    document.getElementById(mcqId).querySelectorAll('.flex.items-center').forEach(row => {
        row.classList.remove('bg-error/10', 'ring-1', 'ring-error', 'rounded-xl');
    });
    document.getElementById(tfId).querySelectorAll('label').forEach(label => {
        label.classList.remove('bg-error/10', 'ring-1', 'ring-error');
    });

    if (type === 'MCQ') {
        const selected = form.querySelector('input[name="correct_option"]:checked');
        const selectedLetter = selected?.value;
        const selectedInput = selectedLetter
            ? form.querySelector(`input[name="option_${selectedLetter}"]`)
            : null;

        if (!selected || !selectedInput?.value.trim()) {
            // Highlight all MCQ radio rows in red
            document.getElementById(mcqId).querySelectorAll('.flex.items-center').forEach(row => {
                row.classList.add('bg-error/10', 'ring-1', 'ring-error', 'rounded-xl');
            });
            errorEl.classList.remove('hidden');
            errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }
    } else {
        const selected = form.querySelector('input[name="correct_tf"]:checked');
        if (!selected) {
            // Highlight both T/F labels in red
            document.getElementById(tfId).querySelectorAll('label').forEach(label => {
                label.classList.add('bg-error/10', 'ring-1', 'ring-error');
            });
            errorEl.classList.remove('hidden');
            errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return false;
        }
    }

    errorEl.classList.add('hidden');
    return true;
}

async function addCategory() {
    const input = document.getElementById('newCategoryInput');
    const errorEl = document.getElementById('categoryError');
    const errorText = document.getElementById('categoryErrorText');
    const name = input.value.trim();

    if (!name) {
        errorText.textContent = 'Please enter a category name.';
        errorEl.classList.remove('hidden');
        return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    const res = await fetch('/categories/add/', { method: 'POST', body: formData });
    const data = await res.json();

    if (!data.ok) {
        errorText.textContent = data.error;
        errorEl.classList.remove('hidden');
        return;
    }

    errorEl.classList.add('hidden');
    input.value = '';

    // Remove empty message if present
    const emptyMsg = document.getElementById('emptyCategoryMsg');
    if (emptyMsg) emptyMsg.remove();

    // Add to category list in modal
    const list = document.getElementById('categoryList');
    list.insertAdjacentHTML('beforeend', `
        <li class="flex items-center justify-between py-3" id="cat-item-${data.id}">
            <span class="text-sm font-semibold text-on-surface">${data.name}</span>
            <button type="button" onclick="deleteCategory(${data.id}, '${data.name}')"
                    class="p-1.5 hover:bg-error/10 text-error rounded-lg transition-colors">
                <span class="material-symbols-outlined text-base">delete</span>
            </button>
        </li>
    `);

    // Add to both category dropdowns
    const option = `<option value="${data.id}">${data.name}</option>`;
    document.getElementById('categorySelect').insertAdjacentHTML('beforeend', option);
    document.getElementById('editCategory').insertAdjacentHTML('beforeend',
        `<option value="${data.id}" data-name="${data.name}">${data.name}</option>`);
}

async function deleteCategory(id, name) {
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', getCSRFToken());

    const res = await fetch(`/categories/${id}/delete/`, { method: 'POST', body: formData });
    const data = await res.json();

    if (!data.ok) {
        alert(data.error);
        return;
    }

    // Remove from modal list
    document.getElementById(`cat-item-${id}`)?.remove();

    // Remove from both dropdowns
    document.querySelectorAll(`#categorySelect option[value="${id}"], #editCategory option[value="${id}"]`)
        .forEach(o => o.remove());
}
function resetAddModal() {
    document.querySelector('#questionModal textarea[name="text"]').value = '';
    document.querySelectorAll('#questionModal input[type="text"]').forEach(i => i.value = '');
    document.querySelectorAll('#questionModal input[type="radio"]').forEach(r => r.checked = false);
    document.querySelector('#questionModal select[name="question_type"]').value = 'MCQ';
    switchLayout('MCQ');
}