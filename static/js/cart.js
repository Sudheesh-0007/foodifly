document.addEventListener('DOMContentLoaded', function() {
    const qtyContainers = document.querySelectorAll('.quantity-picker');

    qtyContainers.forEach(container => {
        const minusBtn = container.querySelector('.qty-btn:first-child');
        const plusBtn = container.querySelector('.qty-btn:last-child');
        const valSpan = container.querySelector('.qty-val');

        plusBtn.addEventListener('click', () => {
            let val = parseInt(valSpan.textContent);
            valSpan.textContent = val + 1;
        });

        minusBtn.addEventListener('click', () => {
            let val = parseInt(valSpan.textContent);
            if (val > 1) {
                valSpan.textContent = val - 1;
            }
        });
    });
});