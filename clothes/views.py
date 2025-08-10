from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm  
from django.views.decorators.http import require_POST
from django.utils import timezone
import logging
from decimal import Decimal

from .models import (
    UserProfile, Product, Order, OrderItem, Recommendation, 
    UserInteraction, Cart, Testimonial, About
)
from .forms import (
    SearchForm, ContactForm, TestimonialForm, 
    CustomUserCreationForm, CustomUserChangeForm, 
    UserProfileForm, AddToCartForm, PasswordChangeForm
)

# ================ MAIN PAGES ================
def opening(request):
    """View for the opening page"""
    return render(request, 'opening.html')

def home(request):
    products = Product.objects.all()
    testimonials = Testimonial.objects.all()
    abouts = About.objects.all() 
    return render(request, 'home.html', {'products': products, 'abouts': abouts, 'testimonials': testimonials})

def privacy_policy(request):
    """View for privacy policy page"""
    return render(request, 'privacy_policy.html')

def refund_policy(request):
    """View for refund policy page"""
    return render(request, 'refund_policy.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def search(request):
    query = request.GET.get('query', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query)
        )
    else:
        products = Product.objects.all()
    return render(request, 'search.html', {'products': products, 'query': query})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Fetch 4 related products (same category, exclude current product)
    related_products = Product.objects.filter(
        subcategory=product.subcategory
    ).exclude(id=product.id)[:6]  # Limit to 4 items
    
    if request.user.is_authenticated:
        track_interaction(request.user, product, 'view')
    
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,  # Pass to template
    })

def product_list(request, category):
    products = Product.objects.filter(category=category)
    return render(request, 'product_list.html', {'products': products, 'category': category.capitalize()})

def submit_testimonial(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = TestimonialForm()
    return render(request, 'submit_testimonial.html', {'form': form})

# ================ AUTHENTICATION ================
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            return redirect('signin')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'signin.html', {'form': form})

@login_required
def profile(request):
    user_form = CustomUserChangeForm(instance=request.user)
    password_form = PasswordChangeForm(user=request.user)
    profile_form = UserProfileForm(instance=request.user.userprofile)
    
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile')
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                new_password = password_form.cleaned_data['new_password']
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password changed successfully. Please log in again.")
                return redirect('signin')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'profile.html', {'user_form': user_form, 'profile_form': profile_form, 'password_form': password_form})

def signout(request):
    logout(request)
    return redirect('home')

# ================ SHOPPING CART & CHECKOUT ================

import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

stripe.api_key = settings.STRIPE_SECRET_KEY

# SHOPPING
def shop(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'shop.html', {'products': products})

@require_POST
@login_required
def add_to_cart(request, product_id):
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))

    # Fetch the product or return a 404 if it doesn't exist
    product = get_object_or_404(Product, id=product_id)

    # Validate stock availability
    if product.stock < quantity:
        return JsonResponse({'error': 'Not enough stock available.'}, status=400)

    # Check if the cart item already exists
    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
        size=size
    )

    if not created:
        # Update the quantity, but ensure it doesn't exceed available stock
        if cart_item.quantity + quantity > product.stock:
            return JsonResponse({'error': 'Not enough stock available.'}, status=400)
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    # Optionally reduce the product stock (if you want to reserve stock immediately)
    product.stock -= quantity
    product.save()

    # Handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart_count = Cart.objects.filter(user=request.user).count()
        return JsonResponse({'cart_count': cart_count, 'success': 'Product added to cart successfully.'})

    # Redirect to the cart page for non-AJAX requests
    return redirect('cart')

@login_required
def update_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size')
        cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.size = size
            cart_item.save()
        cart_items = Cart.objects.filter(user=request.user)
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        if quantity == 0:
            subtotal = 0
        else:
            subtotal = cart_item.product.price * cart_item.quantity
        return JsonResponse({'success': True, 'subtotal': subtotal, 'total_amount': total_amount})

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_amount': total_amount})

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)
    shipping_cost = Decimal('5.00')
    total_with_shipping = total_amount + shipping_cost
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'shipping_cost': shipping_cost,
        'total_with_shipping': total_with_shipping,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'checkout.html', context)

@login_required
def confirm_order(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('cart')
            
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        # Get form data
        payment_method = request.POST.get('payment-method')
        selected_bank = request.POST.get('selected_bank')
        payment_screenshot = request.FILES.get('payment_screenshot')
        shipping_address = request.POST.get('shipping_address')
        billing_address = request.POST.get('billing_address')
        shipping_cost = Decimal('5.00')  # Standard shipping cost as Decimal
        estimated_delivery_date = timezone.now() + timezone.timedelta(days=7)

        # Validate required fields
        if not shipping_address:
            messages.error(request, 'Shipping address is required.')
            return redirect('checkout')
            
        if payment_method == 'qr_code':
            if not selected_bank:
                messages.error(request, 'Please select a bank for QR code payment.')
                return redirect('checkout')
            if not payment_screenshot:
                messages.error(request, 'Please upload payment screenshot for QR code payment.')
                return redirect('checkout')

        # Handle different payment methods
        if payment_method == 'card':
            payment_method_id = request.POST.get('payment_method_id')
            try:
                # Create a PaymentIntent with the order amount and currency
                intent = stripe.PaymentIntent.create(
                    amount=int((total_amount + shipping_cost) * 100),  # Amount in cents
                    currency='usd',
                    payment_method=payment_method_id,
                    confirmation_method='manual',
                    confirm=True,
                )
                
                if intent.status == 'requires_action':
                    return JsonResponse({
                        'success': True,
                        'requires_action': True,
                        'client_secret': intent.client_secret,
                    })
                elif intent.status == 'succeeded':
                    # Payment succeeded, create the order
                    order = Order(
                        user=request.user, 
                        total_amount=total_amount + shipping_cost, 
                        payment_method=payment_method,
                        shipping_address=shipping_address,
                        billing_address=billing_address or shipping_address,
                        shipping_cost=shipping_cost,
                        estimated_delivery_date=estimated_delivery_date,
                        payment_status='paid',
                        payment_verified_at=timezone.now(),
                        status='paid'
                    )
                    order.save()
                    
                    # Create order items
                    for item in cart_items:
                        order_item = OrderItem(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            size=item.size,
                            color=getattr(item, 'color', ''),
                        )
                        order_item.save()
                    
                    # Clear cart
                    cart_items.delete()
                    
                    # Send confirmation email
                    send_payment_confirmation_email(order)
                    
                    context = {
                        'order': order,
                        'order_items': order.orderitem_set.all(),
                        'total_amount': total_amount + shipping_cost,
                    }
                    return render(request, 'confirm_order.html', context)
                else:
                    return JsonResponse({'error': 'Invalid PaymentIntent status'})
                    
            except stripe.error.CardError as e:
                return JsonResponse({'error': str(e.user_message)})
                
        else:
            # Handle cash or QR code payment
            payment_status = 'pending' if payment_method == 'qr_code' else 'paid'
            order_status = 'pending' if payment_method == 'qr_code' else 'paid'
            
            order = Order(
                user=request.user, 
                total_amount=total_amount + shipping_cost, 
                payment_method=payment_method,
                selected_bank=selected_bank if payment_method == 'qr_code' else None,
                payment_screenshot=payment_screenshot if payment_screenshot else None,
                shipping_address=shipping_address,
                billing_address=billing_address or shipping_address,
                shipping_cost=shipping_cost,
                estimated_delivery_date=estimated_delivery_date,
                payment_status=payment_status,
                status=order_status,
                payment_verified_at=timezone.now() if payment_method == 'cash' else None,
            )
            order.save()
            
            # Create order items
            for item in cart_items:
                order_item = OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    size=item.size,
                    color=getattr(item, 'color', ''),
                )
                order_item.save()
            
            # Clear cart
            cart_items.delete()
            
            # Send notifications based on payment method
            if payment_method == 'qr_code':
                # Send notification to admin for manual verification
                send_payment_notification(order)
                messages.success(
                    request, 
                    'Order placed successfully! Your payment is being verified. You will receive confirmation once verified.'
                )
            else:
                # Cash payment - send confirmation
                send_payment_confirmation_email(order)
                messages.success(request, 'Order placed successfully!')
            
            context = {
                'order': order,
                'order_items': order.orderitem_set.all(),
                'total_amount': total_amount + shipping_cost,
                'payment_pending': payment_method == 'qr_code',
            }
            return render(request, 'confirm_order.html', context)
    return redirect('checkout')

# ================ PRODUCT CATEGORIES ================
# Main Category Pages
def men(request):
    products = Product.objects.filter(category='men')
    return render(request, 'men.html', {'products': products})

def women(request):
    products = Product.objects.filter(category='women')
    return render(request, 'women.html', {'products': products})

# Men's Subcategories
def men_shirts(request):
    products = Product.objects.filter(category='men', subcategory='shirts')
    return render(request, 'men/men_shirts.html', {'products': products})

def men_tshirts(request):
    products = Product.objects.filter(category='men', subcategory='t_shirts')
    return render(request, 'men/men_t_shirts.html', {'products': products})

def men_polo_shirts(request):
    products = Product.objects.filter(category='men', subcategory='polo_shirts')
    return render(request, 'men/men_polo_shirts.html', {'products': products})

def men_blazers(request):
    products = Product.objects.filter(category='men', subcategory='blazers')
    return render(request, 'men/men_blazers.html', {'products': products})

def men_jackets(request):
    products = Product.objects.filter(category='men', subcategory='jackets')
    return render(request, 'men/men_jackets.html', {'products': products})

def men_hoodies_sweatshirts(request):
    products = Product.objects.filter(category='men', subcategory='hoodies_sweatshirts')
    return render(request, 'men/men_hoodies_sweatshirts.html', {'products': products})

def men_sweaters_cardigans(request):
    products = Product.objects.filter(category='men', subcategory='sweaters_cardigans')
    return render(request, 'men/men_sweaters_cardigans.html', {'products': products})

def men_jeans(request):
    products = Product.objects.filter(category='men', subcategory='jeans')
    return render(request, 'men/men_jeans.html', {'products': products})

def men_trousers(request):
    products = Product.objects.filter(category='men', subcategory='trousers')
    return render(request, 'men/men_trousers.html', {'products': products})

def men_shorts(request):
    products = Product.objects.filter(category='men', subcategory='shorts')
    return render(request, 'men/men_shorts.html', {'products': products})

def men_shoes(request):
    products = Product.objects.filter(category='men', subcategory='shoes')
    return render(request, 'men/men_shoes.html', {'products': products})

def men_bags(request):
    products = Product.objects.filter(category='men', subcategory='bags')
    return render(request, 'men/men_bags.html', {'products': products})

def men_accessories(request):
    products = Product.objects.filter(category='men', subcategory='accessories')
    return render(request, 'men/men_accessories.html', {'products': products})

def men_perfume(request):
    products = Product.objects.filter(category='men', subcategory='perfume')
    return render(request, 'men/men_perfume.html', {'products': products})

# Women's Subcategories
def women_shirts(request):
    products = Product.objects.filter(category='women', subcategory='shirts')
    return render(request, 'women/women_shirts.html', {'products': products})

def women_tshirts(request):
    products = Product.objects.filter(category='women', subcategory='t_shirts')
    return render(request, 'women/women_t_shirts.html', {'products': products})

def women_tops(request):
    products = Product.objects.filter(category='women', subcategory='tops')
    return render(request, 'women/women_tops.html', {'products': products})

def women_dresses(request):
    products = Product.objects.filter(category='women', subcategory='dresses')
    return render(request, 'women/women_dresses.html', {'products': products})

def women_polo_shirts(request):
    products = Product.objects.filter(category='women', subcategory='polo_shirts')
    return render(request, 'women/women_polo_shirts.html', {'products': products})

def women_blazers(request):
    products = Product.objects.filter(category='women', subcategory='blazers')
    return render(request, 'women/women_blazers.html', {'products': products})

def women_jackets(request):
    products = Product.objects.filter(category='women', subcategory='jackets')
    return render(request, 'women/women_jackets.html', {'products': products})

def women_hoodies_sweatshirts(request):
    products = Product.objects.filter(category='women', subcategory='hoodies_sweatshirts')
    return render(request, 'women/women_hoodies_sweatshirts.html', {'products': products})

def women_sweaters_cardigans(request):
    products = Product.objects.filter(category='women', subcategory='sweaters_cardigans')
    return render(request, 'women/women_sweaters_cardigans.html', {'products': products})

def women_shorts(request):
    products = Product.objects.filter(category='women', subcategory='shorts')
    return render(request, 'women/women_shorts.html', {'products': products})

def women_jeans(request):
    products = Product.objects.filter(category='women', subcategory='jeans')
    return render(request, 'women/women_jeans.html', {'products': products})

def women_trousers(request):
    products = Product.objects.filter(category='women', subcategory='trousers')
    return render(request, 'women/women_trousers.html', {'products': products})

def women_shoes(request):
    products = Product.objects.filter(category='women', subcategory='shoes')
    return render(request, 'women/women_shoes.html', {'products': products})

def women_bags(request):
    products = Product.objects.filter(category='women', subcategory='bags')
    return render(request, 'women/women_bags.html', {'products': products})

def women_accessories(request):
    products = Product.objects.filter(category='women', subcategory='accessories')
    return render(request, 'women/women_accessories.html', {'products': products})

def women_perfume(request):
    products = Product.objects.filter(category='women', subcategory='perfume')
    return render(request, 'women/women_perfume.html', {'products': products})

# ================ RECOMMENDATION SYSTEM ================
def track_interaction(user, product, interaction_type):
    UserInteraction.objects.create(
        user=user,
        product=product,
        interaction_type=interaction_type
    )

def content_based_recommendations(user_profile, products):
    recommended_products = products.filter(
        Q(category__icontains=user_profile.style_preferences) |
        Q(subcategory__icontains=user_profile.style_preferences)
    )
    return recommended_products

def collaborative_filtering_recommendations(user, products):
    similar_users = UserInteraction.objects.filter(
        product__in=UserInteraction.objects.filter(user=user).values('product')
    ).exclude(user=user).values('user').distinct()

    recommended_products = Product.objects.filter(
        id__in=UserInteraction.objects.filter(
            user__in=similar_users,
            interaction_type='purchase'
        ).values('product')
    )
    return recommended_products

@login_required
def recommendations(request):
    user_profile = UserProfile.objects.get(user=request.user)
    recommendations = Recommendation.objects.filter(user=request.user)
    recommended_items = []
    for recommendation in recommendations:
        recommended_items.extend(recommendation.recommended_items.all())
    return render(request, 'recommendations.html', {'recommended_items': recommended_items})

def get_recommendations(user):
    user_profile = UserProfile.objects.get(user=user)
    products = Product.objects.all()
    content_based = content_based_recommendations(user_profile, products)
    collaborative = collaborative_filtering_recommendations(user, products)
    return (content_based | collaborative).distinct()


# ================ PAYMENT NOTIFICATION FUNCTIONS ================
def send_payment_confirmation_email(order):
    """Send payment confirmation email to customer"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'✅ Payment Confirmed - Order #{order.order_id}'
        
        payment_method_display = {
            'cash': 'Cash on Delivery',
            'qr_code': 'Mobile Banking (QR Code)',
            'card': 'Credit/Debit Card'
        }.get(order.payment_method, order.payment_method)
        
        message = f"""
╔══════════════════════════════════════════════════════════════╗
║                    PAYMENT CONFIRMATION                      ║
╚══════════════════════════════════════════════════════════════╝

Dear {order.user.get_full_name()},

🎉 Great news! Your payment has been confirmed and your order is being processed.

📋 ORDER DETAILS:
   • Order ID: #{order.order_id}
   • Total Amount: ${order.total_amount}
   • Payment Method: {payment_method_display}
   • Order Date: {order.order_date.strftime('%B %d, %Y at %H:%M')}
   • Payment Status: ✅ CONFIRMED

🚚 SHIPPING INFORMATION:
   • Shipping Address: {order.shipping_address}
   • Estimated Delivery: {order.estimated_delivery_date.strftime('%B %d, %Y') if order.estimated_delivery_date else 'TBD'}
   • Shipping Cost: ${order.shipping_cost}

📦 YOUR ITEMS:
{chr(10).join([f'   • {item.product.name} (Size: {item.size}, Qty: {item.quantity}) - ${item.product.price}' for item in order.orderitem_set.all()])}

📞 NEED HELP?
   If you have any questions about your order, please contact our customer service team.

Thank you for choosing @ARTISAN! We appreciate your business.

═══════════════════════════════════════════════════════════════
This is an automated confirmation email. Please do not reply.
═══════════════════════════════════════════════════════════════
        """
        
        # Send email to customer
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
            [order.user.email],
            fail_silently=False,
        )
        
        print(f"✅ Payment confirmation email sent to {order.user.email} for Order #{order.order_id}")
        
    except Exception as e:
        print(f"❌ Error sending payment confirmation email for Order #{order.order_id}: {e}")
        # Log to file or monitoring service in production
        logger = logging.getLogger(__name__)
        logger.error(f"Payment confirmation email failed for Order #{order.order_id}: {e}")

def send_payment_notification(order):
    """Send payment notification to admin when QR code payment is made"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'🔔 New Payment Verification Required - Order #{order.order_id}'
        bank_name = dict(order.BANK_CHOICES).get(order.selected_bank, 'Unknown Bank')
        
        # Create formatted message
        message = f"""
╔══════════════════════════════════════════════════════════════╗
║                   PAYMENT VERIFICATION REQUIRED             ║
╚══════════════════════════════════════════════════════════════╝

📋 ORDER DETAILS:
   • Order ID: #{order.order_id}
   • Customer: {order.user.get_full_name()} ({order.user.username})
   • Email: {order.user.email}
   • Total Amount: ${order.total_amount}
   • Payment Method: QR Code Payment
   • Bank: {bank_name}
   • Order Date: {order.order_date.strftime('%Y-%m-%d at %H:%M:%S')}

🏠 SHIPPING DETAILS:
   • Shipping Address: {order.shipping_address}
   • Billing Address: {order.billing_address}
   • Shipping Cost: ${order.shipping_cost}
   • Estimated Delivery: {order.estimated_delivery_date}

📱 CUSTOMER CONTACT:
   • Phone: {getattr(order.user.userprofile, 'phone', 'Not provided') if hasattr(order.user, 'userprofile') else 'Not provided'}

📸 PAYMENT SCREENSHOT:
   • Screenshot uploaded: {'Yes' if order.payment_screenshot else 'No'}
   {f'   • File: {order.payment_screenshot.name}' if order.payment_screenshot else ''}

⚡ ACTION REQUIRED:
   1. Verify the payment screenshot in the admin panel
   2. Confirm the payment amount matches: ${order.total_amount}
   3. Update the order status to 'paid' once verified
   4. Customer will be automatically notified of confirmation

🔗 Admin Panel: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}/admin/clothes/order/{order.order_id}/change/

═══════════════════════════════════════════════════════════════
This is an automated notification from your e-commerce system.
Please do not reply to this email.
═══════════════════════════════════════════════════════════════
        """
        
        # Send email to admin
        admin_emails = []
        if hasattr(settings, 'ADMIN_EMAIL'):
            admin_emails.append(settings.ADMIN_EMAIL)
        if hasattr(settings, 'ADMINS') and settings.ADMINS:
            admin_emails.extend([admin[1] for admin in settings.ADMINS])
        
        # Fallback admin email
        if not admin_emails:
            admin_emails = ['admin@example.com']  # Replace with your actual admin email
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
            admin_emails,
            fail_silently=False,
        )
        
        # Log notification for debugging
        print(f"✅ Payment notification sent for Order #{order.order_id}")
        
        # Optional: Send SMS notification (if SMS service is configured)
        if hasattr(settings, 'SMS_ENABLED') and settings.SMS_ENABLED:
            send_sms_notification(order)
            
    except Exception as e:
        print(f"❌ Error sending payment notification for Order #{order.order_id}: {e}")
        # Log to file or monitoring service in production
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Payment notification failed for Order #{order.order_id}: {e}")

def send_sms_notification(order):
    """Send SMS notification for urgent payments (optional)"""
    try:
        # This is a placeholder for SMS integration
        # You can integrate with services like Twilio, AWS SNS, etc.
        bank_name = dict(order.BANK_CHOICES).get(order.selected_bank, 'Unknown Bank')
        
        message = f"🔔 New QR payment verification needed!\nOrder #{order.order_id}\nAmount: ${order.total_amount}\nBank: {bank_name}\nCheck admin panel now."
        
        # Example Twilio integration (commented out):
        # from twilio.rest import Client
        # client = Client(settings.TWILIO_SID, settings.TWILIO_TOKEN)
        # client.messages.create(
        #     body=message,
        #     from_=settings.TWILIO_PHONE,
        #     to=settings.ADMIN_PHONE
        # )
        
        print(f"📱 SMS notification would be sent: {message}")
        
    except Exception as e:
        print(f"❌ SMS notification error: {e}")

def send_slack_notification(order):
    """Send Slack notification for team awareness (optional)"""
    try:
        # This is a placeholder for Slack integration
        # You can use slack_sdk or webhook integration
        
        bank_name = dict(order.BANK_CHOICES).get(order.selected_bank, 'Unknown Bank')
        
        slack_message = {
            "text": f"🔔 New Payment Verification Required",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New QR Code Payment Received*\n\n*Order:* #{order.order_id}\n*Customer:* {order.user.get_full_name()}\n*Amount:* ${order.total_amount}\n*Bank:* {bank_name}\n\n:warning: *Action needed in admin panel*"
                    }
                }
            ]
        }
        
        # Example webhook implementation (commented out):
        # import requests
        # webhook_url = settings.SLACK_WEBHOOK_URL
        # requests.post(webhook_url, json=slack_message)
        
        print(f"💬 Slack notification would be sent for Order #{order.order_id}")
        
    except Exception as e:
        print(f"❌ Slack notification error: {e}")


@login_required
@require_POST
def check_payment_status(request):
    """AJAX endpoint to check payment status"""
    order_id = request.POST.get('order_id')
    
    try:
        order = Order.objects.get(order_id=order_id, user=request.user)
        
        # In a real implementation, you would check with the bank's API
        # For now, we'll simulate the status check
        
        return JsonResponse({
            'status': order.payment_status,
            'payment_verified_at': order.payment_verified_at.isoformat() if order.payment_verified_at else None,
            'order_status': order.status,
        })
        
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


@login_required
def verify_payment(request, order_id):
    """Admin view to manually verify QR code payments"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    try:
        order = Order.objects.get(order_id=order_id)
        
        if request.method == 'POST':
            action = request.POST.get('action')
            
            if action == 'verify':
                order.payment_status = 'paid'
                order.payment_verified_at = timezone.now()
                order.status = 'paid'
                order.save()
                
                # Send confirmation email to customer
                send_payment_confirmation_email(order)
                
                return JsonResponse({'success': True, 'message': 'Payment verified successfully'})
                
            elif action == 'reject':
                order.payment_status = 'failed'
                order.save()
                
                return JsonResponse({'success': True, 'message': 'Payment rejected'})
        
        context = {
            'order': order,
            'order_items': order.orderitem_set.all(),
        }
        return render(request, 'admin/verify_payment.html', context)
        
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)


def send_payment_confirmation_email(order):
    """Send payment confirmation email to customer"""
    try:
        subject = f'Payment Confirmed - Order #{order.order_id}'
        
        message = f"""
        Dear {order.user.get_full_name()},
        
        Your payment for Order #{order.order_id} has been confirmed!
        
        Order Details:
        - Total Amount: ${order.total_amount}
        - Payment Method: {order.get_payment_method_display()}
        - Bank: {dict(order.BANK_CHOICES).get(order.selected_bank, '')}
        - Estimated Delivery: {order.estimated_delivery_date}
        
        Your order is now being processed and will be shipped soon.
        
        Thank you for your purchase!
        
        Best regards,
        CSR Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.user.email],
            fail_silently=True,
        )
        
    except Exception as e:
        print(f"Error sending confirmation email: {e}")


# ================ WEBHOOK FOR BANK NOTIFICATIONS ================
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def bank_payment_webhook(request):
    """Webhook endpoint for receiving payment notifications from banks"""
    if request.method == 'POST':
        try:
            # Parse the webhook data (format depends on bank's API)
            data = json.loads(request.body)
            
            # Verify webhook signature (implement according to bank's documentation)
            # if not verify_webhook_signature(request, data):
            #     return JsonResponse({'error': 'Invalid signature'}, status=400)
            
            # Extract payment information
            transaction_id = data.get('transaction_id')
            amount = data.get('amount')
            reference = data.get('reference')  # This could be your order ID
            status = data.get('status')
            
            # Find the order
            try:
                order_id = reference.replace('ORDER-', '')  # Assuming reference format
                order = Order.objects.get(order_id=order_id)
                
                if status == 'success' and float(amount) == float(order.total_amount):
                    order.payment_status = 'paid'
                    order.payment_verified_at = timezone.now()
                    order.status = 'paid'
                    order.save()
                    
                    # Send confirmation to customer
                    send_payment_confirmation_email(order)
                    
                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'error': 'Payment verification failed'}, status=400)
                    
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Order not found'}, status=404)
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)