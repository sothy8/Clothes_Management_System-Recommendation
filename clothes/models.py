from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True, help_text="Height in centimeters")
    weight = models.FloatField(blank=True, null=True, help_text="Weight in kilograms")
    body_shape = models.CharField(max_length=50, blank=True, null=True, choices=[
        ('hourglass', 'Hourglass'),
        ('pear', 'Pear'),
        ('apple', 'Apple'),
        ('rectangle', 'Rectangle'),
    ])
    style_preferences = models.CharField(max_length=100, help_text="Comma-separated preferences", blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name or self.last_name else f"{self.user.username}'s Profile"

# Product Model
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
    ]
    SUBCATEGORY_CHOICES = [
        ('shirts', 'Shirts'),
        ('t_shirts', 'T-Shirts'),
        ('polo_shirts', 'Polo Shirt'),
        ('jeans', 'Jeans'),
        ('jackets', 'Jackets'),
        ('blazers', 'Blazers'),
        ('dresses', 'Dresses'),
        ('trousers', 'Trousers'),
        ('hoodies_sweatshirts', 'Hoodies | Sweatshirts'),
        ('sweaters_cardigans', 'Sweater | Cardigans'),
        ('tops', 'Tops'),
        ('shorts', 'Shorts'),
        ('shoes', 'Shoes'),
        ('bags', 'Bags'),
        ('accessories', 'Accessories'),
        ('perfume', 'Perfume'),
        
    ]
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]
    
    product_id = models.CharField(max_length=50, unique=True)  # Barcode or unique ID
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=50, choices=SUBCATEGORY_CHOICES)
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True) 
    stock = models.PositiveIntegerField(default=0)  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=50, choices=SIZE_CHOICES)  # Size options
    image_name = models.CharField(max_length=100, blank=True, null=True)  

    # def available_sizes(self):
    #     # Example: Return all sizes as available
    #     return self.SIZE_CHOICES
    
    # Automatically generate SKU if not provided
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.category[:3].upper()}-{self.subcategory[:3].upper()}-{self.id or ''}".strip('-')
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} (SKU: {self.sku}, Stock: {self.stock}, {self.get_size_display()})"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.size}, {self.quantity})"

#Feedback from users
class About(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    image = models.ImageField(upload_to='static/abouts/', blank=True, null=True)

    def __str__(self):
        return self.name

#Feedback from users
class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    feedback = models.TextField()
    image = models.ImageField(upload_to='static/testimonials/', blank=True, null=True)

    def __str__(self):
        return self.name

# Order Model
class Order(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('qr_code', 'QR Code'),
        ('card', 'Credit/Debit Card'),
    ]
    BANK_CHOICES = [
        ('aba', 'ABA Bank'),
        ('canadia', 'CANADIA Bank'),
        ('aceleda', 'ACELEDA Bank'),
    ]
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the user who placed the order
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='pending')
    selected_bank = models.CharField(max_length=50, choices=BANK_CHOICES, blank=True, null=True)  # Selected bank for QR payment
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', blank=True, null=True)  # Payment confirmation screenshot
    shipping_address = models.TextField(blank=True, null=True)  # Shipping address
    billing_address = models.TextField(blank=True, null=True)   # Billing address
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Shipping cost
    estimated_delivery_date = models.DateField(blank=True, null=True)  # Estimated delivery date
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='pending')  # Order status
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='pending')  # Payment verification status
    payment_verified_at = models.DateTimeField(blank=True, null=True)  # When payment was verified

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

    def update_total_amount(self):
        self.total_amount = sum(item.product.price * item.quantity for item in self.orderitem_set.all())
        self.save()


# OrderItem Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, null=True)
    color = models.CharField(max_length=20, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Reduce stock when an order item is created
        if not self.pk:  # Only reduce stock for new items
            if self.product.stock >= self.quantity:
                self.product.stock -= self.quantity
                self.product.save()
            else:
                raise ValueError("Not enough stock available.")
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"


# Recommendation Model
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Links to the user
    recommended_items = models.ManyToManyField(Product)  # List of recommended items
    recommendation_score = models.FloatField(help_text="Score indicating the strength of the recommendation")

    def __str__(self):
        return f"Recommendation for {self.user.username} (Score: {self.recommendation_score})"
    
# Contact Model
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name
    
from django.db import models
from django.contrib.auth.models import User

class UserInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=50, choices=[
        ('view', 'View'),
        ('purchase', 'Purchase'),
    ])
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.interaction_type}"


# Django Signals to automatically create UserProfile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email
        )
