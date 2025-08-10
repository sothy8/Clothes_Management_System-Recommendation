from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument."""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError, Exception):
        return 0

@register.filter
def mul(value, arg):
    """Alias for multiply filter."""
    return multiply(value, arg)

@register.filter
def add_decimal(value, arg):
    """Add two values with decimal precision."""
    try:
        return Decimal(str(value)) + Decimal(str(arg))
    except (ValueError, TypeError, Exception):
        return value

@register.filter
def percentage(value, percent):
    """Calculate percentage of a value."""
    try:
        return Decimal(str(value)) * (Decimal(str(percent)) / 100)
    except (ValueError, TypeError, Exception):
        return 0

@register.filter
def tax_amount(value, rate=0.1):
    """Calculate tax amount."""
    try:
        return Decimal(str(value)) * Decimal(str(rate))
    except (ValueError, TypeError, Exception):
        return 0

@register.filter
def calc_tax(subtotal, shipping_cost=5.00):
    """Calculate 10% tax on subtotal + shipping."""
    try:
        total_before_tax = Decimal(str(subtotal)) + Decimal(str(shipping_cost))
        return total_before_tax * Decimal('0.1')
    except (ValueError, TypeError, Exception):
        return 0

@register.filter  
def calc_total_with_tax(subtotal, shipping_cost=5.00):
    """Calculate total with 10% tax on subtotal + shipping."""
    try:
        total_before_tax = Decimal(str(subtotal)) + Decimal(str(shipping_cost))
        tax = total_before_tax * Decimal('0.1')
        return total_before_tax + tax
    except (ValueError, TypeError, Exception):
        return 0
