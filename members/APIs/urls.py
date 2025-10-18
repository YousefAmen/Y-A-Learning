from django.urls import path
from members.APIs import views

urlpatterns = [
    path("user-profile/", views.user_profile, name="user-profile"),
    path("edit-profile/", views.edit_user_profile, name="edit-profile"),
    path("delete-profile/", views.delete_user_profile, name="delete-profile"),
    path("links/", views.instructor_links, name="instructor-links"),
    path("create-social-links/", views.create_social_links, name="create-social-links"),
    path(
        "update-social-links/<slug:slug>/",
        views.update_social_links,
        name="create-social-links",
    ),
    path(
        "delete-social-links/<slug:slug>/",
        views.delete_social_links,
        name="create-social-links",
    ),
]
