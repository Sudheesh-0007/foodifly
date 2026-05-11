document.addEventListener('DOMContentLoaded', function() {
    // Handle card removal
    const closeButtons = document.querySelectorAll('.btn-close-wishlist');
    
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const card = this.closest('.wishlist-card');
            card.style.opacity = '0';
            card.style.transform = 'translateX(20px)';
            setTimeout(() => {
                card.remove();
            }, 300);
        });
    });

    // Simple Navbar toggle
    const navLinks = document.querySelectorAll('.account-nav .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if(!this.classList.contains('logout-link')) {
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
});