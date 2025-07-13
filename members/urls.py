from django.urls import path

from .views import (
    UserPublicProfile,
    delete_profile,
    edit_profile,
    select_role,
    user_profile,
)

app_name = 'members'

urlpatterns = [
  path('account_type/',select_role,name = 'select_role'),
  path('user/<slug:slug>/<str:token>/',user_profile,name = 'user_profile'),
  path('edit-profile/<slug:slug>/<str:role>/<str:token>/',edit_profile,name = 'edit_profile'),
  path('delete-profile/<slug:slug>/<str:role>/<str:token>/',delete_profile,name = 'delete_profile'),
  path('user-public-profile/<slug:slug>/<str:token>/',UserPublicProfile.as_view(),name = 'user_public_profile'),
]