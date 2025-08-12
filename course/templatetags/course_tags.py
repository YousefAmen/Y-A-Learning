from datetime import timedelta

from django import template
from ..models import Category, Course
from django.db.models import Count

register = template.Library()


@register.filter
def format_duration(value):
    if not value:
        return "0:00"
    total_sconds = int(value.total_seconds())
    hours, remainder = divmod(total_sconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


@register.filter
def top_categorise(value):
    return Category.objects.annotate(top=Count("course")).order_by("-top")
