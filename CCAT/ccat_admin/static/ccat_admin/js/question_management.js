    // Global variables for abstract reasoning
    let abstractOptionCount = 8;

    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
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

    // --- Integrated Question Management Logic ---

    function checkCategory(select) {
        const catName = select.options[select.selectedIndex].text.toLowerCase();
        const isAbstract = catName.includes('abstract');

        const formTypeInput = document.getElementById('formTypeInput');
        const qTypeWrapper = document.getElementById('qTypeWrapper');
        const standardTextWrapper = document.getElementById('standardTextWrapper');
        const abstractImageWrapper = document.getElementById('abstractImageWrapper');
        const mcqLayout = document.getElementById('mcqLayout');
        const tfLayout = document.getElementById('tfLayout');
        const abstractOptionsLayout = document.getElementById('abstractOptionsLayout');
        const modalTitle = document.getElementById('modalTitle');
        const questionTextarea = document.getElementById('questionTextarea');

        if (isAbstract) {
            formTypeInput.value = 'abstract';
            modalTitle.innerText = 'Add Abstract Reasoning Question';

            // Show Abstract fields
            abstractImageWrapper.classList.remove('hidden');
            abstractOptionsLayout.classList.remove('hidden');

            // Hide Standard fields
            qTypeWrapper.classList.add('hidden');
            standardTextWrapper.classList.add('hidden');
            mcqLayout.classList.add('hidden');
            tfLayout.classList.add('hidden');

            // Clear and disable text field
            questionTextarea.value = '';
            questionTextarea.disabled = true;



            rebuildAbstractOptions();
        } else {
            formTypeInput.value = 'standard';
            modalTitle.innerText = 'Add New Question';

            // Show Standard fields
            qTypeWrapper.classList.remove('hidden');
            standardTextWrapper.classList.remove('hidden');
            switchLayout(document.getElementById('qTypeSelect').value);

            // RE-ENABLE the textarea
            questionTextarea.disabled = false;

            // Hide Abstract fields
            abstractImageWrapper.classList.add('hidden');
            abstractOptionsLayout.classList.add('hidden');
        }
    }

    function switchLayout(type) {
        const mcq = document.getElementById('mcqLayout');
        const tf = document.getElementById('tfLayout');
        const isAbstract = document.getElementById('formTypeInput').value === 'abstract';
        
        if (isAbstract) return; // Abstract stays in its own layout

        if (type === 'MCQ') {
            mcq.classList.remove('hidden');
            tf.classList.add('hidden');
        } else {
            mcq.classList.add('hidden');
            tf.classList.remove('hidden');
        }
    }

    function handleQuestionSubmit(form) {
        const type = document.getElementById('formTypeInput').value;
        const errorEl = document.getElementById('addAnswerError');
        const errorMsg = document.getElementById('errorMsgText');

        const showErr = (msg) => {
            errorMsg.innerText = msg;
            errorEl.classList.remove('hidden');
        };

        errorEl.classList.add('hidden');

        if (type === 'abstract') {
            const qImg = document.getElementById('abstractQuestionImage').files.length > 0;
            const correct = document.getElementById('abstractCorrectSelect').value;

            if (!qImg) { showErr("Please upload a question image."); return false; }
            if (!correct) { showErr("Please select the correct answer."); return false; }

            for (let i = 1; i <= abstractOptionCount; i++) {
                const fileInput = document.getElementById(`opt_img_input_${i}`);
                if (!fileInput || fileInput.files.length === 0) {
                    showErr(`Please upload image for Option ${i}.`); return false;
                }
            }
        } else {
            const qText = document.getElementById('questionTextarea').value.trim();
            if (!qText) { showErr("Please enter a question text."); return false; }

            const qType = document.getElementById('qTypeSelect').value;
            if (qType === 'MCQ') {
                const correct = form.querySelector('input[name="correct_option"]:checked');
                if (!correct) { showErr("Please select the correct MCQ option."); return false; }

                const selectedLetter = correct.value;
                const selectedText = form.querySelector(`input[name="option_${selectedLetter}"]`).value.trim();
                if (!selectedText) { showErr(`Selected option ${selectedLetter} has no text.`); return false; }

                // Also check all filled options have text if marked correct
                for (const letter of ['A','B','C','D']) {
                    const radio = form.querySelector(`input[name="correct_option"][value="${letter}"]`);
                    const text = form.querySelector(`input[name="option_${letter}"]`).value.trim();
                    if (radio.checked && !text) {
                        showErr(`Option ${letter} is selected as correct but has no text.`); return false;
                    }
                }
            } else {
                const correct = form.querySelector('input[name="correct_tf"]:checked');
                if (!correct) { showErr("Please select True or False."); return false; }
            }
        }

        return true;
    }
    // --- Abstract Reasoning Specific Functions ---

    function changeAbstractOptionCount(delta) {
        const newCount = abstractOptionCount + delta;
        if (newCount >= 2 && newCount <= 12) {
            abstractOptionCount = newCount;
            document.getElementById('abstractOptionCountLabel').innerText = abstractOptionCount;
            rebuildAbstractOptions();
        }
    }

    function rebuildAbstractOptions() {
        const grid = document.getElementById('abstractOptionsGrid');
        const select = document.getElementById('abstractCorrectSelect');
        const currentCorrect = select.value;

        grid.innerHTML = '';
        select.innerHTML = '<option value="">-- Choose Correct --</option>';

        for (let i = 1; i <= abstractOptionCount; i++) {
            // Add to Grid
            const item = document.createElement('div');
            item.className = 'relative group';
            item.innerHTML = `
                <div class="aspect-square bg-surface-container rounded-lg border border-outline-variant/20 flex flex-col items-center justify-center cursor-pointer hover:bg-primary/5 transition-all overflow-hidden"
                     onclick="document.getElementById('opt_img_input_${i}').click()">
                    <span class="text-[10px] font-black text-outline/40 absolute top-1 left-2">${i}</span>
                    <span id="opt_icon_${i}" class="material-symbols-outlined text-outline/30 text-xl">add_a_photo</span>
                    <img id="opt_preview_${i}" src="" class="hidden w-full h-full object-contain">
                    <input type="file" name="option_image_${i}" id="opt_img_input_${i}" accept="image/*" class="hidden" onchange="previewAbstractOption(this, ${i})">
                </div>
            `;
            grid.appendChild(item);

            // Add to Select
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = `Option ${i}`;
            if (currentCorrect == i) opt.selected = true;
            select.appendChild(opt);
        }
    }

    function previewAbstractQuestion(input) {
        const preview = document.getElementById('abstractQuestionPreview');
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = e => {
                preview.src = e.target.result;
                preview.classList.remove('hidden');
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    function previewAbstractOption(input, index) {
        const preview = document.getElementById(`opt_preview_${index}`);
        const icon = document.getElementById(`opt_icon_${index}`);
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = e => {
                preview.src = e.target.result;
                preview.classList.remove('hidden');
                icon.classList.add('hidden');
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    function resetAddModal() {
        const form = document.querySelector('#questionModal form');
        form.reset();
        
        // Reset Standard previews/states
        document.getElementById('addAnswerError').classList.add('hidden');
        
        // Reset Abstract previews
        const qPreview = document.getElementById('abstractQuestionPreview');
        qPreview.src = '';
        qPreview.classList.add('hidden');
        
        abstractOptionCount = 8;
        document.getElementById('abstractOptionCountLabel').innerText = 8;
        
        // Default back to standard unless "Abstract" is first category
        checkCategory(document.getElementById('categorySelect'));
    }

    // --- Other Shared Functions (Search, Category Management, Delete, Edit) ---

    function filterQuestions() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        const catFilter = document.getElementById('categoryFilter').value;
        const rows = document.querySelectorAll('.question-row');

        rows.forEach(row => {
            const text = row.innerText.toLowerCase();
            const category = row.dataset.category;
            const matchesQuery = text.includes(query);
            const matchesCat = (catFilter === 'all' || category === catFilter);

            row.style.display = (matchesQuery && matchesCat) ? '' : 'none';
        });
    }

    function addCategory() {
        const input = document.getElementById('newCategoryInput');
        const name = input.value.trim();
        const errorEl = document.getElementById('categoryError');
        const errorText = document.getElementById('categoryErrorText');

        if (!name) return;

        fetch('/categories/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken()
            },
            body: `name=${encodeURIComponent(name)}`
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                location.reload();
            } else {
                errorText.innerText = data.error;
                errorEl.classList.remove('hidden');
            }
        });
    }

    function deleteCategory(id, name) {
        if (!confirm(`Are you sure you want to delete "${name}"?`)) return;

        fetch(`/categories/${id}/delete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken()
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                location.reload();
            } else {
                alert(data.error);
            }
        });
    }

    function openDeleteModal(btn, preview) {
        const form = document.getElementById('deleteForm');
        form.action = btn.dataset.deleteUrl;
        document.getElementById('deleteQuestionPreview').innerText = preview;
        toggleModal('deleteModal', true);
    }

    function openEditModal(id, text, type, category, btn) {
        const form = document.getElementById('editForm');
        form.action = btn.dataset.editUrl;
        
        document.getElementById('editText').value = text;
        document.getElementById('editType').value = type;
        
        // Select category
        const catSelect = document.getElementById('editCategory');
        let isAbstract = false;
        for (let opt of catSelect.options) {
            if (opt.text === category) {
                opt.selected = true;
                isAbstract = opt.text.toLowerCase().includes('abstract');
                break;
            }
        }

        const row = btn.closest('tr');
        const options = JSON.parse(row.dataset.options);
        const qImage = row.dataset.image;

        if (isAbstract) {
            checkEditCategory(catSelect);
            const preview = document.getElementById('editAbstractQuestionPreview');
            if (qImage) {
                preview.src = qImage;
                preview.classList.remove('hidden');
            } else {
                preview.classList.add('hidden');
            }
            rebuildEditAbstractOptions(options);
        } else {
            checkEditCategory(catSelect);
            if (type === 'MCQ') {
                options.forEach(opt => {
                    const input = document.getElementById(`editOption${opt.letter}`);
                    const radio = document.getElementById(`editCorrect${opt.letter}`);
                    if (input) input.value = opt.text;
                    if (radio) radio.checked = opt.correct;
                });
                switchEditLayout('MCQ');
            } else {
                const isTrueCorrect = options.find(o => o.text === 'True')?.correct;
                if (isTrueCorrect) {
                    document.getElementById('editCorrectTrue').checked = true;
                } else {
                    document.getElementById('editCorrectFalse').checked = true;
                }
                switchEditLayout('SS');
            }
        }

        toggleModal('editModal', true);
    }

    function checkEditCategory(select) {
        const catName = select.options[select.selectedIndex].text.toLowerCase();
        const isAbstract = catName.includes('abstract');

        const qTypeWrapper = document.getElementById('editQTypeWrapper');
        const standardTextWrapper = document.getElementById('editStandardTextWrapper');
        const abstractImageWrapper = document.getElementById('editAbstractImageWrapper');
        const mcqLayout = document.getElementById('editMcqLayout');
        const tfLayout = document.getElementById('editTfLayout');
        const abstractOptionsLayout = document.getElementById('editAbstractOptionsLayout');
        const questionTextarea = document.getElementById('editText');

        if (isAbstract) {
            abstractImageWrapper.classList.remove('hidden');
            abstractOptionsLayout.classList.remove('hidden');
            qTypeWrapper.classList.add('hidden');
            standardTextWrapper.classList.add('hidden');
            mcqLayout.classList.add('hidden');
            tfLayout.classList.add('hidden');
            questionTextarea.disabled = true;
        } else {
            qTypeWrapper.classList.remove('hidden');
            standardTextWrapper.classList.remove('hidden');
            switchEditLayout(document.getElementById('editType').value);
            questionTextarea.disabled = false;
            abstractImageWrapper.classList.add('hidden');
            abstractOptionsLayout.classList.add('hidden');
        }
    }

    function rebuildEditAbstractOptions(options) {
        const grid = document.getElementById('editAbstractOptionsGrid');
        const select = document.getElementById('editAbstractCorrectSelect');

        grid.innerHTML = '';
        select.innerHTML = '<option value="">-- Choose Correct --</option>';

        options.forEach((opt, idx) => {
            const i = idx + 1;
            // Add to Grid
            const item = document.createElement('div');
            item.className = 'relative group';
            item.innerHTML = `
                <div class="aspect-square bg-surface-container rounded-lg border border-outline-variant/20 flex flex-col items-center justify-center cursor-pointer hover:bg-primary/5 transition-all overflow-hidden"
                     onclick="document.getElementById('edit_opt_img_input_${i}').click()">
                    <span class="text-[10px] font-black text-outline/40 absolute top-1 left-2">${i}</span>
                    <span id="edit_opt_icon_${i}" class="material-symbols-outlined text-outline/30 text-xl ${opt.image ? 'hidden' : ''}">add_a_photo</span>
                    <img id="edit_opt_preview_${i}" src="${opt.image || ''}" class="${opt.image ? '' : 'hidden'} w-full h-full object-contain">
                    <input type="file" name="option_image_${i}" id="edit_opt_img_input_${i}" accept="image/*" class="hidden" onchange="previewEditAbstractOption(this, ${i})">
                </div>
            `;
            grid.appendChild(item);

            // Add to Select
            const o = document.createElement('option');
            o.value = i;
            o.textContent = `Option ${i}`;
            if (opt.correct) o.selected = true;
            select.appendChild(o);
        });
    }

    function previewEditAbstractQuestion(input) {
        const preview = document.getElementById('editAbstractQuestionPreview');
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = e => {
                preview.src = e.target.result;
                preview.classList.remove('hidden');
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    function previewEditAbstractOption(input, index) {
        const preview = document.getElementById(`edit_opt_preview_${index}`);
        const icon = document.getElementById(`edit_opt_icon_${index}`);
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = e => {
                preview.src = e.target.result;
                preview.classList.remove('hidden');
                icon.classList.add('hidden');
            };
            reader.readAsDataURL(input.files[0]);
        }
    }

    function switchEditLayout(type) {
        const mcq = document.getElementById('editMcqLayout');
        const tf = document.getElementById('editTfLayout');
        const catSelect = document.getElementById('editCategory');
        const isAbstract = catSelect.options[catSelect.selectedIndex].text.toLowerCase().includes('abstract');
        
        if (isAbstract) return;

        if (type === 'MCQ') {
            mcq.classList.remove('hidden');
            tf.classList.add('hidden');
        } else {
            mcq.classList.add('hidden');
            tf.classList.remove('hidden');
        }
    }

    function validateAnswer(form) {
        const catSelect = form.querySelector('[name="category"]');
        const catName = catSelect.options[catSelect.selectedIndex].text.toLowerCase();
        const isAbstract = catName.includes('abstract');
        const errorEl = document.getElementById('editAnswerError');
        const errorSpan = errorEl.querySelector('span:last-child');

        const showErr = (msg) => {
            errorSpan.innerText = msg;
            errorEl.classList.remove('hidden');
        };

        errorEl.classList.add('hidden');

        if (isAbstract) {
            const correct = form.querySelector('[name="abstract_correct_option"]').value;
            if (!correct) { showErr("Please select the correct answer."); return false; }
        } else {
            const qText = form.querySelector('[name="text"]').value.trim();
            if (!qText) { showErr("Please enter a question text."); return false; }

            const type = form.querySelector('[name="question_type"]').value;
            if (type === 'MCQ') {
                const correct = form.querySelector('input[name="correct_option"]:checked');
                if (!correct) { showErr("Please select the correct MCQ option."); return false; }

                const selectedLetter = correct.value;
                const selectedText = form.querySelector(`input[name="option_${selectedLetter}"]`).value.trim();
                if (!selectedText) { showErr(`Selected option ${selectedLetter} has no text.`); return false; }
            } else {
                const correct = form.querySelector('input[name="correct_tf"]:checked');
                if (!correct) { showErr("Please select True or False."); return false; }
            }
        }

        return true;
    }
