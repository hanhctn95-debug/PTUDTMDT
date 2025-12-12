from django import template

register = template.Library()

@register.filter
def format_price(value):
    try:
        price = int(value)
        # Format number with commas and then replace with dots
        return f'{price:,}'.replace(',', '.') + ' đ'
    except (ValueError, TypeError):
        # In case the value is not a valid number, return it as is
        return value
