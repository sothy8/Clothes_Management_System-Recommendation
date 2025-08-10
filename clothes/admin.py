from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
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
    list_display = [
        'order_id', 'user', 'order_date', 'total_amount', 
        'payment_method', 'selected_bank', 'payment_status_badge', 
        'status', 'payment_actions'
    ]
    search_fields = ('order_id', 'user__username', 'user__email')
    list_filter = (
        'payment_method', 'selected_bank', 'payment_status', 
        'status', 'order_date', 'payment_verified_at'
    )
    readonly_fields = (
        'order_id', 'order_date', 'payment_verified_at', 
        'payment_screenshot_preview'
    )
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'order_date', 'total_amount', 'status')
        }),
        ('Payment Details', {
            'fields': (
                'payment_method', 'selected_bank', 'payment_status', 
                'payment_verified_at', 'payment_screenshot_preview', 'payment_screenshot'
            )
        }),
        ('Shipping Information', {
            'fields': ('shipping_address', 'billing_address', 'shipping_cost', 'estimated_delivery_date'),
            'classes': ('collapse',)
        }),
    )
    
    def payment_status_badge(self, obj):
        colors = {
            'pending': '#fbbf24',
            'paid': '#10b981',
            'failed': '#ef4444',
            'refunded': '#6b7280'
        }
        color = colors.get(obj.payment_status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, obj.get_payment_status_display().upper()
        )
    payment_status_badge.short_description = 'Payment Status'
    
    def payment_actions(self, obj):
        if obj.payment_method == 'qr_code' and obj.payment_status == 'pending':
            verify_url = reverse('verify_payment', args=[obj.order_id])
            return format_html(
                '<a href="{}" class="button" style="background-color: #10b981; '
                'color: white; padding: 4px 12px; text-decoration: none; '
                'border-radius: 4px; font-size: 12px;">Verify Payment</a>',
                verify_url
            )
        elif obj.payment_status == 'paid':
            return format_html('<span style="color: #10b981;">✓ Verified</span>')
        return '-'
    payment_actions.short_description = 'Actions'
    
    def payment_screenshot_preview(self, obj):
        if obj.payment_screenshot:
            return format_html(
                '<img src="{}" style="max-width: 200px; max-height: 200px; '
                'border-radius: 8px; border: 1px solid #ddd;" />',
                obj.payment_screenshot.url
            )
        return 'No screenshot uploaded'
    payment_screenshot_preview.short_description = 'Payment Screenshot'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    # Custom actions
    actions = ['mark_as_paid', 'mark_as_shipped']
    
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(
            payment_status='paid',
            payment_verified_at=timezone.now(),
            status='paid'
        )
        self.message_user(request, f'{updated} orders marked as paid.')
    mark_as_paid.short_description = "Mark selected orders as paid"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.filter(payment_status='paid').update(status='shipped')
        self.message_user(request, f'{updated} orders marked as shipped.')
    mark_as_shipped.short_description = "Mark selected paid orders as shipped"


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


