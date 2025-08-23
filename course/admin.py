from django.contrib import admin

from .models import (
    Category,
    Contact,
    # Rating,
    Course,
    Enrollment,
    LearningOutcomes,
    Lesson,
    Module,
    Review,
)


class CourseAdmin(admin.ModelAdmin):
    list_filter = [
        "is_puplished",
        "created_at",
        "updated_at",
        "is_free",
        "discount_price",
    ]
    ordering = ["title", "is_puplished", "created_at"]
    prepopulated_fields = {"slug": ("title",)}
    # readonly_fields = ['slug','instructor']
    # exclude = ['token']


class EnrollmentAdmin(admin.ModelAdmin):
    list_filter = ["enrollment_date"]


class ModuleAdmin(admin.ModelAdmin):
    list_filter = ["is_published", "created_at", "updated_at"]
    ordering = ["title", "created_at", "updated_at"]


# class RatingAdmin(admin.ModelAdmin):
#     list_filter = ["created_at"]
#     ordering = ["rate", "created_at"]


class ReviewAdmin(admin.ModelAdmin):
    list_filter = ["created_at"]
    ordering = ["created_at", "updated_at"]
    readonly_fields = ["slug"]


class LessonAdmin(admin.ModelAdmin):
    list_filter = ["added_at"]
    ordering = ["title", "added_at"]
    readonly_fields = ["slug"]


class ContactAdmin(admin.ModelAdmin):
    list_filter = ["created_at"]
    ordering = ["created_at"]
    readonly_fields = ["token"]


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
# admin.site.register(Rating, RatingAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(Category)
admin.site.register(LearningOutcomes)
admin.site.register(Contact, ContactAdmin)
