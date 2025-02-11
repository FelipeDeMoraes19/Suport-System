# ticket/templatetags/file_extension.py
from django import template

register = template.Library()

@register.filter
def file_extension(filename):
    """Returns the file extension from a filename."""
    return filename.split('.')[-1] if '.' in filename else ''

@register.filter
def endswith_custom(value, suffix):
    """Check if a string ends with the given suffix."""
    return value.endswith(suffix)
