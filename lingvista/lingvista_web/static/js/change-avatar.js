// change-avatar.js
document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('.hidden-file-input');
    fileInputs.forEach(input => {
        const button = input.previousElementSibling.previousElementSibling;
        const fileNameSpan = document.getElementById(`file-name-${input.id}`);

        button.addEventListener('click', function(e) {
            e.preventDefault();
            input.click();
        });

        input.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileNameSpan.textContent = this.files[0].name;
            } else {
                fileNameSpan.textContent = 'No file chosen';
            }
        });
    });
});
