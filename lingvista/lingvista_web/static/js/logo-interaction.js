// logo-interaction.js
document.addEventListener('DOMContentLoaded', function() {
    const logo = document.getElementById('clickable-logo');
    const bubble = document.getElementById('speech-bubble');

    if (!logo || !bubble) {
        console.error('Required elements not found');
        return;
    }

    const phrases = [
        "Learn with joy!",
        "Knowledge is power!",
        "Discover Russian language!",
        "Lingvista - your guide in the world of languages.",
        "Unlock your potential!",
        "Every word is a new opportunity!",
        "Language opens doors!",
        "Learn smarter, not harder!",
        "Your journey starts here!",
        "Become a global citizen!",
        "Lingvista - where words come alive!",
        "Say 'hello' to fluency!",
        "No more language barriers!",
        "Tag your study buddy!",
        "Which phrase inspires you?"
    ];

    let hideTimeout;

    logo.addEventListener('click', function() {
        // Clear any pending hide operations
        clearTimeout(hideTimeout);

        // Hide bubble immediately
        bubble.classList.remove('visible');

        // After fade-out completes, show new phrase
        setTimeout(() => {
            const randomPhrase = phrases[Math.floor(Math.random() * phrases.length)];
            bubble.textContent = randomPhrase;
            bubble.classList.add('visible');

            // Auto-hide after 3 seconds
            hideTimeout = setTimeout(() => {
                bubble.classList.remove('visible');
            }, 3000);
        }, 300);
    });
});