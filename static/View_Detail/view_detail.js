document.addEventListener('DOMContentLoaded', function() {
    // Thumbnail image switching
    const thumbnails = document.querySelectorAll('.thumbnail');
    const mainImage = document.getElementById('mainProductImage');
    
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            // Remove active class from all thumbnails
            thumbnails.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked thumbnail
            this.classList.add('active');
            
            // Update main image
            mainImage.src = this.src;
        });
    });
    
    // Quantity selector buttons
    const quantityInput = document.getElementById('quantity');
    const minusBtn = document.querySelector('.quantity-btn.minus');
    const plusBtn = document.querySelector('.quantity-btn.plus');
    
    minusBtn.addEventListener('click', function() {
        let value = parseInt(quantityInput.value);
        if (value > 1) {
            quantityInput.value = value - 1;
        }
    });
    
    plusBtn.addEventListener('click', function() {
        let value = parseInt(quantityInput.value);
        if (value < 10) { // Assuming max quantity is 10
            quantityInput.value = value + 1;
        }
    });
    
    // Size guide modal
    const sizeGuideBtn = document.getElementById('sizeGuideBtn');
    const sizeGuideModal = document.getElementById('sizeGuideModal');
    const closeModal = document.querySelector('.close-modal');
    
    sizeGuideBtn.addEventListener('click', function() {
        sizeGuideModal.style.display = 'block';
    });
    
    closeModal.addEventListener('click', function() {
        sizeGuideModal.style.display = 'none';
    });
    
    window.addEventListener('click', function(event) {
        if (event.target === sizeGuideModal) {
            sizeGuideModal.style.display = 'none';
        }
    });
    
    // Tab functionality
    const tabLinks = document.querySelectorAll('.tabs-nav a');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all tabs
            document.querySelectorAll('.tabs-nav li').forEach(li => {
                li.classList.remove('active');
            });
            
            // Add active class to current tab
            this.parentElement.classList.add('active');
            
            // Hide all tab panes
            document.querySelectorAll('.tab-pane').forEach(pane => {
                pane.classList.remove('active');
            });
            
            // Show current tab pane
            const targetPane = document.querySelector(this.getAttribute('href'));
            targetPane.classList.add('active');
        });
    });
    
    // Wishlist button functionality
    const wishlistBtn = document.querySelector('.wishlist-btn');
    
    wishlistBtn.addEventListener('click', function() {
        // This would be replaced with actual wishlist functionality
        this.innerHTML = '<i class="fas fa-heart"></i> Added to Wishlist';
        this.style.backgroundColor = '#f8f8f8';
        
        setTimeout(() => {
            this.innerHTML = '<i class="far fa-heart"></i> Add to Wishlist';
            this.style.backgroundColor = 'white';
        }, 2000);
    });
});