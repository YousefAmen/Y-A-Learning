import django_filters
from .models import Course
from django.db.models import Sum, Count


class CourseFilter(django_filters.FilterSet):
    level = django_filters.MultipleChoiceFilter(
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
        ]
    )
    price = django_filters.RangeFilter()
    ordering = django_filters.ChoiceFilter(
        label="Sort By",
        method="filter_ordering",
        choices=[
            ("newest", "Newest First"),
            ("oldest", "Oldest First"),
            ("best_seller", "Best Seller"),
            ("top_rated", "Top_Rated"),
        ],
    )

    def filter_ordering(self, queryset, name, value):
        queryset = queryset.filter(is_published=True)
        if value == "newest":
            return queryset.order_by("-created_at")
        elif value == "oldest":
            return queryset.order_by("created_at")
        elif value == "best_seller":
            return queryset.annotate(enroll=Count("course_enrollments")).order_by(
                "-enroll"
            )
        elif value == "top_rated":
            return queryset.annotate(rate=Count("course_reviews")).order_by("-rate")
        return queryset.annotate(
            enroll=Count("course_enrollments"), rate=Count("course_reviews__rate")
        ).order_by("-enroll", "-rate")

    class Meta:
        model = Course

        fields = ["level", "category", "price", "ordering"]
