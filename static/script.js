document.addEventListener('DOMContentLoaded', function () {
    // Swiper Initialization for Hero Section
    const heroSwiper = new Swiper(".swiper-container", {
        loop: true,
        autoplay: {
            delay: 5000, // Change slide every 5 seconds
            disableOnInteraction: false,
        },
        speed: 1000, // Smooth transition speed
        slidesPerView: 3, // Show 3 slides per view
        slidesPerGroup: 3, // Slide 3 slides at a time
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
        breakpoints: {
            0: {
                slidesPerView: 1,
                slidesPerGroup: 1,
            },
            768: {
                slidesPerView: 2,
                slidesPerGroup: 2,
            },
            1024: {
                slidesPerView: 3,
                slidesPerGroup: 3,
            },
        }
    });

    const testimonialSwiper = new Swiper(".slider-wrapper", {
        loop: true,
        autoplay: {
            delay: 5000,
            disableOnInteraction: false,
        },
        speed: 1000,
        slidesPerView: 1,
        slidesPerGroup: 1,
        pagination: {
            el: ".swiper-pagination",
            clickable: true,
        },
        navigation: {
            nextEl: ".swiper-button-next",
            prevEl: ".swiper-button-prev",
        },
    });

    // Menu toggle for mobile view
    const menuToggleButton = document.getElementById("menu-toggle-button");
    const navMenu = document.getElementById("nav-menu");
    const overlay = document.getElementById("overlay");

    menuToggleButton.addEventListener("click", function () {
        navMenu.classList.toggle("active");
        overlay.classList.toggle("active");
    });

    // Close menu if overlay is clicked
    overlay.addEventListener("click", function () {
        navMenu.classList.remove("active");
        overlay.classList.remove("active");
    });

    // Smooth scroll for anchor links
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(function (link) {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const targetId = link.getAttribute("href").substring(1);
            const targetElement = document.getElementById(targetId);

            window.scrollTo({
                top: targetElement.offsetTop - 50, // Adding a little offset for better readability
                behavior: "smooth"
            });
        });
    });

    // Updating the Cart Counter dynamically when an item is added
    const cartCounter = document.getElementById("cart-counter");
    let cartItems = 0;  // Initialize cart items

    // Function to update cart counter
    function updateCartCounter() {
        cartItems += 1;  // Increment cart items by 1
        cartCounter.textContent = cartItems;
    }

    // Add event listener to "Add to Cart" buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const productId = this.getAttribute('data-product-id');
            document.getElementById('product_id').value = productId;
            document.getElementById('add-to-cart-popup').classList.remove('hidden');
        });
    });

    // Close the popup when "Close" is clicked
    document.getElementById('close-popup').addEventListener('click', function () {
        document.getElementById('add-to-cart-popup').classList.add('hidden');
    });

    // Handle form submission
    document.getElementById('add-to-cart-form').addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch("{% url 'add_to_cart' %}", {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Item added to cart!');
                document.getElementById('add-to-cart-popup').classList.add('hidden');
                updateCartCounter();
            } else {
                alert('Failed to add item to cart. Please try again.');
            }
        })
        .catch(() => {
            alert('An error occurred. Please try again.');
        });
    });

    // Scroll Animation for Fade-in Effect
    const fadeInElements = document.querySelectorAll('.fade-in');
    function handleScroll() {
        fadeInElements.forEach(function (element) {
            const rect = element.getBoundingClientRect();
            if (rect.top < window.innerHeight * 0.75) {
                element.classList.add("visible");
            } else {
                element.classList.remove("visible");
            }
        });
    }
    window.addEventListener("scroll", handleScroll);
    handleScroll(); // Initial check on load
});