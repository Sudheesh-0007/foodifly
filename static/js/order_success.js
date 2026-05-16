document.addEventListener('DOMContentLoaded', function() {
    // Fade in the summary card for a premium feel
    const summaryCard = document.querySelector('.success-summary-card');
    summaryCard.style.opacity = '0';
    summaryCard.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
        summaryCard.style.transition = 'all 0.8s ease-out';
        summaryCard.style.opacity = '1';
        summaryCard.style.transform = 'translateY(0)';
    }, 200);
});