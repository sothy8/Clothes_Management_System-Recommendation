const stripe = Stripe('{{ STRIPE_PUBLISHABLE_KEY }}');
        const elements = stripe.elements();
        const cardElement = elements.create('card');
        cardElement.mount('#card-element');

        const form = document.getElementById('payment-form');
        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            // Disable the submit button to prevent multiple submissions
            form.querySelector('button[type="submit"]').disabled = true;

            // Get the selected payment method
            const paymentMethod = document.querySelector('input[name="payment-method"]:checked').value;

            // Add the payment method to the form as a hidden input
            const paymentMethodInput = document.createElement('input');
            paymentMethodInput.setAttribute('type', 'hidden');
            paymentMethodInput.setAttribute('name', 'payment_method');
            paymentMethodInput.setAttribute('value', paymentMethod);
            form.appendChild(paymentMethodInput);

            // Handle cash or QR code payment
            if (paymentMethod === 'cash' || paymentMethod === 'qr-code') {
                form.submit();
                return;
            }

            // Handle card payment with Stripe
            const { error, paymentMethod: stripePaymentMethod } = await stripe.createPaymentMethod({
                type: 'card',
                card: cardElement,
            });

            if (error) {
                // Show error to the user
                document.getElementById('card-errors').textContent = error.message;
                form.querySelector('button[type="submit"]').disabled = false;
            } else {
                // Send paymentMethod.id to your server
                fetch('/confirm_order/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': '{{ csrf_token }}' },
                    body: JSON.stringify({ payment_method_id: stripePaymentMethod.id }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.requires_action) {
                            // Handle 3D Secure authentication
                            stripe.confirmCardPayment(data.client_secret)
                                .then(result => {
                                    if (result.error) {
                                        // Show error to the user
                                        document.getElementById('card-errors').textContent = result.error.message;
                                        form.querySelector('button[type="submit"]').disabled = false;
                                    } else {
                                        // Payment succeeded, redirect to success page
                                        window.location.href = '/confirm_order/';
                                    }
                                });
                        } else {
                            // Payment succeeded without additional action, redirect to success page
                            window.location.href = '/confirm_order/';
                        }
                    } else {
                        // Show error to the user
                        document.getElementById('card-errors').textContent = data.error;
                        form.querySelector('button[type="submit"]').disabled = false;
                    }
                });
            }
        });

        $(document).ready(function() {
            $('input[name="payment-method"]').change(function() {
                $('.payment-details').hide();
                if (this.value === 'cash') {
                    $('#cash-details').show();
                } else if (this.value === 'qr-code') {
                    $('#qr-code-details').show();
                } else if (this.value === 'card') {
                    $('#card-details').show();
                }
            });
            $('input[name="payment-method"]:checked').trigger('change');
        });