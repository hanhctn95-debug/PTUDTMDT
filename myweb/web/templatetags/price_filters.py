from django import template
from decimal import Decimal, InvalidOperation

register = template.Library()

@register.filter
def format_price(value):
    if value is None:
        return "0 đ" # Return a default value for None
    
    try:
        # Ensure value is a Decimal type for consistent handling
        if not isinstance(value, Decimal):
            value = Decimal(str(value)) # Convert to string then to Decimal to handle floats/ints
            
        # Convert to integer for formatting (dropping decimal places for prices)
        # Use quantize to round properly before converting to int
        price = int(value.quantize(Decimal('1.'), rounding='ROUND_HALF_UP'))
        
        # Format number with thousands separator (comma for Python's locale formatting)
        # Then replace comma with dot for Vietnamese locale and append "đ"
        return f'{price:,}'.replace(',', '.') + ' đ'
    except (ValueError, TypeError, AttributeError, InvalidOperation):
        # If conversion fails, return the original value as a string (with 'đ' if it was a Decimal)
        # This ensures the template doesn't crash but shows the problematic value.
        if isinstance(value, Decimal):
            return f"{value} đ"
        return str(value)