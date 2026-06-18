document.addEventListener('DOMContentLoaded', function() {
    // Row Item Destructive Action Handler Interception
    const deleteTriggers = document.querySelectorAll('.btn-delete-trigger');
    
    deleteTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const rowContextElement = this.closest('tr');
            const couponCodeText = rowContextElement.querySelector('.coupon-code-badge').textContent;
            const couponId = this.getAttribute('data-id');


        });
    });
});