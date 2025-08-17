from django.contrib import admin
from .models import Instructor, SocialLinks, Student


class StudentAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("first_name", "last_name")}


class InstructorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("first_name", "last_name")}


admin.site.register(Student, StudentAdmin)

admin.site.register(Instructor, InstructorAdmin)
admin.site.register(SocialLinks)
