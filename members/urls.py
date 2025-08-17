from django.urls import path

from .views import (
    CreateLink,
    DeleteLink,
    UpdateLink,
    UserPublicProfile,
    delete_profile,
    edit_profile,
    instructor_courses,
    select_role,
    user_profile,
    instructor_top_courses,
)

app_name = "members"

urlpatterns = [
    path("account_type/", select_role, name="select_role"),
    path("user/<slug:slug>/<str:token>/", user_profile, name="user_profile"),
    path(
        "edit-profile/<slug:slug>/<str:role>/<str:token>/",
        edit_profile,
        name="edit_profile",
    ),
    path(
        "delete-profile/<slug:slug>/<str:role>/<str:token>/",
        delete_profile,
        name="delete_profile",
    ),
    path(
        "user-public-profile/<slug:slug>/<str:token>/",
        UserPublicProfile.as_view(),
        name="user_public_profile",
    ),
    path("my-top-courses/", instructor_top_courses, name="instructor_top_courses"),
    path("my-courses/", instructor_courses, name="instructor_courses"),
    path("add-link/", CreateLink.as_view(), name="add_link"),
    path("update-link/<str:name>/", UpdateLink.as_view(), name="update_link"),
    path("delete-link/<str:name>/", DeleteLink.as_view(), name="delete_link"),
]
