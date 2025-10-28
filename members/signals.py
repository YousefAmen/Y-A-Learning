from allauth.socialaccount.signals import social_account_added
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.shortcuts import redirect
from django.urls import reverse

from .models import Instructor, Student

user_signed_up = Signal()


@receiver(user_signed_up)
def create_profile(sender, user, signup_data, **kwargs):

    if signup_data["role"] == "instructor":
        profile = Instructor.objects.create(
            user=user,
            teaching_exe=1,
        )

    else:

        profile = Student.objects.create(user=user)
