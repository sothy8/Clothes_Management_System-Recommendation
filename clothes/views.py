from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm  
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import (
    UserProfile, Product, Order, OrderItem, Recommendation, 
    UserInteraction, Cart, Testimonial,
)
from .forms import (
    SearchForm, ContactForm, TestimonialForm, 
    CustomUserCreationForm, CustomUserChangeForm, 
    UserProfileForm, AddToCartForm, PasswordChangeForm
)

# ================ MAIN PAGES ================
def home(request):
    products = Product.objects.all()
    testimonials = Testimonial.objects.all()
    return render(request, 'home.html', {'products': products, 'testimonials': testimonials})

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
    return render(request, 'search_results.html', {'products': products, 'query': query})

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

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = CustomUserChangeForm(request.POST, instance=request.user)
            profile_form = UserProfileForm(request.POST, instance=request.user.userprofile)
            if user_form.is_valid():
                user_form.save()
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
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'checkout.html', context)

@login_required
def confirm_order(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        total_amount = sum(item.product.price * item.quantity for item in cart_items)
        
        payment_method = request.POST.get('payment-method')
        shipping_address = request.POST.get('shipping_address')
        billing_address = request.POST.get('billing_address')
        shipping_cost = 5.00  # Example shipping cost
        estimated_delivery_date = timezone.now() + timezone.timedelta(days=7)  # Example delivery date

        if payment_method == 'card':
            payment_method_id = request.POST.get('payment_method_id')
            try:
                # Create a PaymentIntent with the order amount and currency
                intent = stripe.PaymentIntent.create(
                    amount=int(total_amount * 100),  # Amount in cents
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
                    order = Order(user=request.user, 
                                  total_amount=total_amount, 
                                  payment_method=payment_method,
                                  shipping_address=shipping_address,
                                  billing_address=billing_address,
                                  shipping_cost=shipping_cost,
                                  estimated_delivery_date=estimated_delivery_date,
                                  )
                    order.save()
                    for item in cart_items:
                        order_item = OrderItem(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            size=item.size,
                        )
                        order_item.save()
                    cart_items.delete()
                    context = {
                        'order': order,
                        'order_items': order.orderitem_set.all(),
                        'total_amount': total_amount,
                    }
                    return render(request, 'confirm_order.html', context)
                else:
                    return JsonResponse({'error': 'Invalid PaymentIntent status'})

            except stripe.error.CardError as e:
                return JsonResponse({'error': str(e.user_message)})
        else:
            # Handle cash or QR code payment
            order = Order(user=request.user, 
                          total_amount=total_amount, 
                          payment_method=payment_method,
                          shipping_address=shipping_address,
                          billing_address=billing_address,
                          shipping_cost=shipping_cost,
                          estimated_delivery_date=estimated_delivery_date,
                          )
            order.save()
            for item in cart_items:
                order_item = OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    size=item.size,
                )
                order_item.save()
            cart_items.delete()
            context = {
                'order': order,
                'order_items': order.orderitem_set.all(),
                'total_amount': total_amount,
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
    return render(request, 'men_shirts.html', {'products': products})

def men_tshirts(request):
    products = Product.objects.filter(category='men', subcategory='t_shirts')
    return render(request, 'men_t_shirts.html', {'products': products})

def men_polo_shirts(request):
    products = Product.objects.filter(category='men', subcategory='polo_shirts')
    return render(request, 'men_polo_shirts.html', {'products': products})

def men_blazers(request):
    products = Product.objects.filter(category='men', subcategory='blazers')
    return render(request, 'men_blazers.html', {'products': products})

def men_jackets(request):
    products = Product.objects.filter(category='men', subcategory='jackets')
    return render(request, 'men_jackets.html', {'products': products})

def men_hoodies_sweatshirts(request):
    products = Product.objects.filter(category='men', subcategory='hoodies_sweatshirts')
    return render(request, 'men_hoodies_sweatshirts.html', {'products': products})

def men_sweaters_cardigans(request):
    products = Product.objects.filter(category='men', subcategory='sweaters_cardigans')
    return render(request, 'men_sweaters_cardigans.html', {'products': products})

def men_jeans(request):
    products = Product.objects.filter(category='men', subcategory='jeans')
    return render(request, 'men_jeans.html', {'products': products})

def men_trousers(request):
    products = Product.objects.filter(category='men', subcategory='trousers')
    return render(request, 'men_trousers.html', {'products': products})

def men_shorts(request):
    products = Product.objects.filter(category='men', subcategory='shorts')
    return render(request, 'men_shorts.html', {'products': products})

def men_shoes(request):
    products = Product.objects.filter(category='men', subcategory='shoes')
    return render(request, 'men_shoes.html', {'products': products})

def men_bags(request):
    products = Product.objects.filter(category='men', subcategory='bags')
    return render(request, 'men_bags.html', {'products': products})

def men_accessories(request):
    products = Product.objects.filter(category='men', subcategory='accessories')
    return render(request, 'men_accessories.html', {'products': products})

def men_perfume(request):
    products = Product.objects.filter(category='men', subcategory='perfume')
    return render(request, 'men_perfume.html', {'products': products})

# Women's Subcategories
def women_shirts(request):
    products = Product.objects.filter(category='women', subcategory='shirts')
    return render(request, 'women_shirts.html', {'products': products})

def women_tshirts(request):
    products = Product.objects.filter(category='women', subcategory='t_shirts')
    return render(request, 'women_t_shirts.html', {'products': products})

def women_tops(request):
    products = Product.objects.filter(category='women', subcategory='tops')
    return render(request, 'women_tops.html', {'products': products})

def women_dresses(request):
    products = Product.objects.filter(category='women', subcategory='dresses')
    return render(request, 'women_dresses.html', {'products': products})

def women_polo_shirts(request):
    products = Product.objects.filter(category='women', subcategory='polo_shirts')
    return render(request, 'women_polo_shirts.html', {'products': products})

def women_blazers(request):
    products = Product.objects.filter(category='women', subcategory='blazers')
    return render(request, 'women_blazers.html', {'products': products})

def women_jackets(request):
    products = Product.objects.filter(category='women', subcategory='jackets')
    return render(request, 'women_jackets.html', {'products': products})

def women_hoodies_sweatshirts(request):
    products = Product.objects.filter(category='women', subcategory='hoodies_sweatshirts')
    return render(request, 'women_hoodies_sweatshirts.html', {'products': products})

def women_sweaters_cardigans(request):
    products = Product.objects.filter(category='women', subcategory='sweaters_cardigans')
    return render(request, 'women_sweaters_cardigans.html', {'products': products})

def women_shorts(request):
    products = Product.objects.filter(category='women', subcategory='shorts')
    return render(request, 'women_shorts.html', {'products': products})

def women_jeans(request):
    products = Product.objects.filter(category='women', subcategory='jeans')
    return render(request, 'women_jeans.html', {'products': products})

def women_trousers(request):
    products = Product.objects.filter(category='women', subcategory='trousers')
    return render(request, 'women_trousers.html', {'products': products})

def women_shoes(request):
    products = Product.objects.filter(category='women', subcategory='shoes')
    return render(request, 'women_shoes.html', {'products': products})

def women_bags(request):
    products = Product.objects.filter(category='women', subcategory='bags')
    return render(request, 'women_bags.html', {'products': products})

def women_accessories(request):
    products = Product.objects.filter(category='women', subcategory='accessories')
    return render(request, 'women_accessories.html', {'products': products})

def women_perfume(request):
    products = Product.objects.filter(category='women', subcategory='perfume')
    return render(request, 'women_perfume.html', {'products': products})

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

