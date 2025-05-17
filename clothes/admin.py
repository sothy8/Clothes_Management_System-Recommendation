from django.contrib import admin
from .models import UserProfile, Product, Order, OrderItem, Recommendation, Testimonial, About
from django.contrib.auth.models import User

# Register UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'email', 'height', 'weight', 'body_shape')
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    list_filter = ('body_shape',)


# Register Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'price', 'get_size_display', 'image_name')
    search_fields = ('name', 'category', 'subcategory')
    list_filter = ('category', 'subcategory', 'size')


# Register Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'order_date', 'total_amount', 'payment_method']
    search_fields = ('order_id', 'user__username')
    list_filter = ('payment_method', 'order_date')


# Register OrderItem
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'size', 'color']
    search_fields = ('order__order_id', 'product__name')
    list_filter = ('order__order_date',)

# Register Recommendation
@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'recommendation_score')
    search_fields = ('user__username',)
    list_filter = ('recommendation_score',)
    filter_horizontal = ('recommended_items',)  
    
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'feedback', 'image')
    search_fields = ('name', 'feedback')
    
@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'image')
    search_fields = ('name', 'position')


