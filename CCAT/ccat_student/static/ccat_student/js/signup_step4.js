document.addEventListener('DOMContentLoaded', function() {
    const selects = [
        document.querySelector('select[name="first_priority"]'),
        document.querySelector('select[name="second_priority"]'),
        document.querySelector('select[name="third_priority"]')
    ];

    function updateOptions() {
        const selectedValues = selects.map(s => s.value).filter(v => v !== "");

        selects.forEach(currentSelect => {
            const options = currentSelect.querySelectorAll('option');
            options.forEach(option => {
                if (option.value === "") return;

                const isSelectedElsewhere = selectedValues.includes(option.value) && currentSelect.value !== option.value;
                option.disabled = isSelectedElsewhere;

                if (isSelectedElsewhere) {
                    if (!option.textContent.includes(" (Chosen)")) {
                        option.textContent += " (Chosen)";
                    }
                } else {
                    option.textContent = option.textContent.replace(" (Chosen)", "");
                }
            });
        });
    }
    selects.forEach(s => s.addEventListener('change', updateOptions));
});