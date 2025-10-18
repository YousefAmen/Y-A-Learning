from django.contrib import admin

from .models import (
    Category,
    Contact,
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


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class EnrollmentAdmin(admin.ModelAdmin):
    list_filter = ["enrollment_date"]


class ModuleAdmin(admin.ModelAdmin):
    list_filter = ["is_published", "created_at", "updated_at"]
    ordering = ["title", "created_at", "updated_at"]
    prepopulated_fields = {"slug": ("title",)}


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


class LearningOutcomesAdmin(admin.ModelAdmin):
    ordering = ["created_at"]
    prepopulated_fields = {"slug": ("description",)}


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Module, ModuleAdmin)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(LearningOutcomes, LearningOutcomesAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Category, CategoryAdmin)
