from datetime import timedelta

from django import template

register = template.Library()
@register.filter
def format_duration(value):
    if not value:
      return '0:00'
    total_sconds = int(value.total_seconds())
    hours,remainder = divmod(total_sconds, 3600)
    minutes,seconds = divmod(remainder,60)
    if hours > 0:
      return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"