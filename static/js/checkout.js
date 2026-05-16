document.addEventListener('DOMContentLoaded', function() {
    // Function to handle selection logic for multiple groups
    const setupSelection = (containerSelector) => {
        const container = document.querySelector(containerSelector);
        if (!container) return;

        const cards = container.querySelectorAll('.selectable-card');
        
        cards.forEach(card => {
            card.addEventListener('click', () => {
                // Remove active class and dots from all in this group
                cards.forEach(c => {
                    c.classList.remove('active');
                    const circle = c.querySelector('.radio-circle');
                    if(circle) circle.innerHTML = '';
                });

                // Add active class and dot to clicked card
                card.classList.add('active');
                const radio = card.querySelector('.radio-circle');
                if(radio) radio.innerHTML = '<div class="dot"></div>';
            });
        });
    };

    // Initialize both sections
    setupSelection('.address-selection');
    setupSelection('.payment-selection');
});