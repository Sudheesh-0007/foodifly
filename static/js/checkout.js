document.addEventListener('DOMContentLoaded', function() {
    // Address and Shipping Selection
    const handleSelection = (selector) => {
        const cards = document.querySelectorAll(selector);
        cards.forEach(card => {
            card.addEventListener('click', () => {
                cards.forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                
                // If it has a radio circle, update the dot
                const radio = card.querySelector('.radio-circle');
                if (radio) {
                    cards.forEach(c => {
                        const r = c.querySelector('.radio-circle');
                        if (r) r.innerHTML = '';
                    });
                    radio.innerHTML = '<div class="dot"></div>';
                }
            });
        });
    };

    handleSelection('.address-selection .selectable-card');
    handleSelection('.method-card');
});