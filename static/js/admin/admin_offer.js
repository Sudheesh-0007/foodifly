document.addEventListener('DOMContentLoaded', function() {
    // 1. Structural Action Tab Selection Handler Toggle Module
    const segmentLinks = document.querySelectorAll('.segment-pills .nav-link');
    segmentLinks.forEach(pill => {
        pill.addEventListener('click', function() {
            segmentLinks.forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            
            // Contextual filtering logic array hooks can execute below
            console.log(`Filtering matrix targeted onto category criterion: ${this.textContent}`);
        });
    });

    // 2. Row Action Management - Interactive Delete Prompts
    const deleteTriggers = document.querySelectorAll('.btn-delete-trigger');
    deleteTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const targetsRowContext = this.closest('tr');
            const targetOfferHeading = targetsRowContext.querySelector('h6').textContent;
            
            if (confirm(`Are you sure you want to permanently strip out this active promotional campaign:\n"${targetOfferHeading}"?`)) {
                targetsRowContext.style.opacity = '0';
                targetsRowContext.style.transform = 'scale(0.95)';
                targetsRowContext.style.transition = 'all 0.35s ease';
                
                setTimeout(() => {
                    targetsRowContext.remove();
                }, 350);
            }
        });
    });

    // 3. New Offer Registration Simulation Modal Trigger Hook
    const createNewBtn = document.querySelector('.btn-add-offer');
    if (createNewBtn) {
        createNewBtn.addEventListener('click', function() {
            console.log("Redirecting system engine flow into localized Campaign Creation Wizard panel...");
        });
    }
});