// Enhanced Payment System JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Stripe if available
    let stripe, elements, cardElement;
    
    if (typeof Stripe !== 'undefined' && window.STRIPE_PUBLISHABLE_KEY) {
        try {
            stripe = Stripe(window.STRIPE_PUBLISHABLE_KEY);
            elements = stripe.elements();
            
            // Create card element with custom styling
            cardElement = elements.create('card', {
                style: {
                    base: {
                        fontSize: '16px',
                        color: '#333',
                        fontFamily: 'Arial, sans-serif',
                        '::placeholder': {
                            color: '#888',
                        },
                        padding: '12px',
                    },
                    invalid: {
                        color: '#dc3545',
                        iconColor: '#dc3545'
                    }
                }
            });
            
            cardElement.mount('#card-element');
            
            // Handle real-time validation errors from the card Element
            cardElement.on('change', function(event) {
                const displayError = document.getElementById('card-errors');
                if (event.error) {
                    displayError.textContent = event.error.message;
                } else {
                    displayError.textContent = '';
                }
            });
        } catch (error) {
            // Stripe initialization error - handle silently
        }
    }

    // QR Code bank images mapping
    const bankQRCodes = {
        'aba': '/static/cart/ABA.png',
        'aceleda': '/static/cart/ACELEDA.png',
        'canadia': '/static/cart/CANADIA.png'
    };

    // Bank names mapping
    const bankNames = {
        'aba': 'ABA Bank',
        'aceleda': 'ACELEDA Bank',
        'canadia': 'CANADIA Bank'
    };

    // Payment method handling
    const paymentMethods = document.querySelectorAll('input[name="payment-method"]');
    const paymentDetails = document.querySelectorAll('.payment-details');

    function showPaymentDetails(selectedMethod) {
        // Hide all payment details
        paymentDetails.forEach(detail => {
            detail.classList.remove('active');
        });
        
        // Show selected payment method details
        const targetDetail = document.getElementById(`${selectedMethod}-details`);
        
        if (targetDetail) {
            setTimeout(() => {
                targetDetail.classList.add('active');
            }, 150);
        }
    }

    // Initialize with default selection
    showPaymentDetails('cash');

    // Handle payment method changes
    paymentMethods.forEach(method => {
        method.addEventListener('change', function() {
            if (this.checked) {
                showPaymentDetails(this.value.replace('_', '-'));
                updateFormValidation(this.value);
            }
        });
    });

    // Bank selection for QR codes
    const bankSelect = document.getElementById('bank-select');
    const qrDisplay = document.getElementById('qr-display');
    const qrImage = document.getElementById('qr-image');
    const selectedBankName = document.getElementById('selected-bank-name');
    const paymentScreenshot = document.getElementById('payment_screenshot');

    if (bankSelect) {
        bankSelect.addEventListener('change', function() {
            const selectedBank = this.value;
            
            if (selectedBank && bankQRCodes[selectedBank]) {
                // Show QR code display
                qrDisplay.style.display = 'block';
                
                // Update QR code image and bank name
                qrImage.src = bankQRCodes[selectedBank];
                qrImage.alt = `${bankNames[selectedBank]} QR Code`;
                selectedBankName.textContent = bankNames[selectedBank];
                
                // Make screenshot upload required
                if (paymentScreenshot) {
                    paymentScreenshot.required = true;
                }
                
                // Smooth scroll to QR code
                setTimeout(() => {
                    qrDisplay.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }, 300);
            } else {
                qrDisplay.style.display = 'none';
                if (paymentScreenshot) {
                    paymentScreenshot.required = false;
                }
            }
        });
    }

    // Form validation based on payment method
    function updateFormValidation(paymentMethod) {
        const shippingAddress = document.getElementById('shipping_address');
        const bankSelect = document.getElementById('bank-select');
        const paymentScreenshot = document.getElementById('payment_screenshot');

        // Shipping address is always required
        if (shippingAddress) {
            shippingAddress.required = true;
        }

        // QR code specific requirements
        if (paymentMethod === 'qr_code') {
            if (bankSelect) {
                bankSelect.required = false; // Handled separately
            }
            if (paymentScreenshot) {
                paymentScreenshot.required = false; // Will be set when bank is selected
            }
        } else {
            // For cash and card, remove QR-specific requirements
            if (bankSelect) {
                bankSelect.required = false;
            }
            if (paymentScreenshot) {
                paymentScreenshot.required = false;
            }
        }
    }

    // Form submission handling
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');

    if (form && submitButton) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const selectedPaymentMethod = document.querySelector('input[name="payment-method"]:checked')?.value;
            
            if (selectedPaymentMethod === 'card') {
                if (stripe && cardElement) {
                    handleStripePayment();
                } else {
                    showError('Card payment is not available. Please choose another payment method.');
                    resetSubmitButton();
                }
            } else {
                handleNonCardPayment();
            }
        });
    }

    async function handleStripePayment() {
        const { error, paymentMethod } = await stripe.createPaymentMethod({
            type: 'card',
            card: cardElement,
        });

        if (error) {
            showError(error.message);
            resetSubmitButton();
            return;
        }

        // Submit to server with payment method
        const formData = new FormData(form);
        formData.append('payment_method_id', paymentMethod.id);

        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': window.CSRF_TOKEN || document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const data = await response.json();
            
            if (data.success) {
                if (data.requires_action) {
                    const { error: confirmError } = await stripe.confirmCardPayment(data.client_secret);
                    if (confirmError) {
                        showError(confirmError.message);
                        resetSubmitButton();
                    } else {
                        // Payment succeeded
                        window.location.href = '/confirm_order/';
                    }
                } else {
                    // Payment succeeded
                    window.location.href = '/confirm_order/';
                }
            } else {
                showError(data.error || 'Payment failed. Please try again.');
                resetSubmitButton();
            }
        } catch (error) {
            showError('Network error. Please check your connection and try again.');
            resetSubmitButton();
        }
    }

    function handleNonCardPayment() {
        // Show loading state
        submitButton.disabled = true;
        submitButton.classList.add('loading');
        
        const selectedPaymentMethod = document.querySelector('input[name="payment-method"]:checked')?.value;
        
        // Validation for QR code payment
        if (selectedPaymentMethod === 'qr_code') {
            const bankSelect = document.getElementById('bank-select');
            const paymentScreenshot = document.getElementById('payment_screenshot');
            
            if (!bankSelect || !bankSelect.value) {
                showError('Please select a bank for QR code payment.');
                resetSubmitButton();
                return;
            }
            
            if (!paymentScreenshot || !paymentScreenshot.files.length) {
                showError('Please upload your payment screenshot.');
                resetSubmitButton();
                return;
            }
        }
        
        // Common validation
        const shippingAddress = document.getElementById('shipping_address');
        
        if (!shippingAddress || !shippingAddress.value.trim()) {
            showError('Please enter your shipping address.');
            resetSubmitButton();
            return;
        }
        
        // Submit form normally for cash and QR code payments
        form.submit();
    }

    function showError(message) {
        // Remove any existing error messages
        const existingError = document.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Create new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.cssText = `
            background-color: #f8d7da;
            color: #721c24;
            padding: 12px 16px;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            margin: 15px 0;
            font-size: 14px;
            font-weight: 500;
        `;
        errorDiv.textContent = message;
        
        // Insert before submit button
        submitButton.parentNode.insertBefore(errorDiv, submitButton);
        
        // Scroll to error message
        errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    function resetSubmitButton() {
        submitButton.disabled = false;
        submitButton.classList.remove('loading');
    }

    // File upload preview
    if (paymentScreenshot) {
        paymentScreenshot.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                // Remove existing preview
                const existingPreview = document.querySelector('.screenshot-preview');
                if (existingPreview) {
                    existingPreview.remove();
                }
                
                // Create preview if it's an image
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const preview = document.createElement('div');
                        preview.className = 'screenshot-preview';
                        preview.innerHTML = `
                            <div style="margin-top: 15px; text-align: center;">
                                <p style="margin-bottom: 10px; font-weight: 600; color: #333;">Preview:</p>
                                <img src="${e.target.result}" 
                                     style="max-width: 200px; max-height: 200px; border-radius: 8px; border: 2px solid #ddd; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" 
                                     alt="Payment screenshot preview">
                                <p style="margin-top: 10px; font-size: 14px; color: #666;">
                                    File: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)
                                </p>
                            </div>
                        `;
                        paymentScreenshot.parentNode.appendChild(preview);
                    };
                    reader.readAsDataURL(file);
                }
            }
        });
    }

    // Auto-fill billing address
    const shippingAddress = document.getElementById('shipping_address');
    const billingAddress = document.getElementById('billing_address');
    
    if (shippingAddress && billingAddress) {
        // Add checkbox to copy shipping to billing
        const copyAddressHTML = `
            <div style="margin-top: 10px;">
                <label style="display: flex; align-items: center; font-weight: normal; cursor: pointer;">
                    <input type="checkbox" id="copy-address" style="margin-right: 8px;">
                    Same as shipping address
                </label>
            </div>
        `;
        billingAddress.parentNode.insertAdjacentHTML('beforeend', copyAddressHTML);
        
        const copyAddressCheckbox = document.getElementById('copy-address');
        copyAddressCheckbox.addEventListener('change', function() {
            if (this.checked) {
                billingAddress.value = shippingAddress.value;
                billingAddress.disabled = true;
            } else {
                billingAddress.disabled = false;
            }
        });
        
        // Update billing when shipping changes (if checkbox is checked)
        shippingAddress.addEventListener('input', function() {
            if (copyAddressCheckbox.checked) {
                billingAddress.value = this.value;
            }
        });
    }
});
