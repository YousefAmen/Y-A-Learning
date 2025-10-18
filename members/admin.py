from django.contrib import admin
from .models import Instructor, SocialLinks, Student
from django.contrib.auth.admin import UserAdmin
from .models import User
from django.contrib.auth.forms import UserChangeForm, UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "role",
            "profile_pic",
            "phone",
            "gender",
            "country",
            "birth_date",
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = ["first_name", "last_name", "is_active", "is_staff"]
    ordering = ("email",)
    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = ["created_at", "updated_at", "slug", "token"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "role",
                    "bio",
                    "gender",
                    "profile_pic",
                    "phone",
                    "country",
                    "birth_date",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
        ("SEO", {"fields": ("slug", "token")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "role",
                    "bio",
                    "gender",
                    "profile_pic",
                    "phone",
                    "country",
                    "birth_date",
                    "created_at",
                    "updated_at",
                    "slug",
                    "token",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


class InstructorAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "bio",
        "gender",
        "profile_pic",
        "phone",
        "birth_date",
        "country",
        "slug",
        "token",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["email", "created_at", "updated_at", "token"]
    prepopulated_fields = {"slug": ("first_name", "last_name")}
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "bio",
                    "profile_pic",
                )
            },
        ),
        (
            "Additional Info",
            {"fields": ("phone", "gender", "country", "birth_date")},
        ),
        (
            "Permissions",
            {"fields": ("groups",)},
        ),
        (
            "SEO",
            {"fields": ("slug", "token")},
        ),
        (
            "Dates",
            {"fields": ("created_at", "updated_at")},
        ),
    )


class StudentAdmin(admin.ModelAdmin):
    list_display = [
        "first_name",
        "last_name",
        "bio",
        "gender",
        "profile_pic",
        "phone",
        "birth_date",
        "country",
        "slug",
        "token",
        "created_at",
        "updated_at",
    ]
    readonly_fields = ["email", "created_at", "updated_at", "token"]
    prepopulated_fields = {"slug": ("first_name", "last_name")}
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "bio",
                    "profile_pic",
                )
            },
        ),
        (
            "Additional Info",
            {"fields": ("phone", "gender", "country", "birth_date")},
        ),
        (
            "SEO",
            {"fields": ("slug", "token")},
        ),
        (
            "Dates",
            {"fields": ("created_at", "updated_at")},
        ),
    )


class SocialLinks_Admin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("link_name",)}


admin.site.register(SocialLinks, SocialLinks_Admin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Instructor, InstructorAdmin)
admin.site.register(Student, StudentAdmin)
