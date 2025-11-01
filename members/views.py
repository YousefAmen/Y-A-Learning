from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from course.models import Course, Enrollment

from .forms import (
    RoleSelectionForm,
    SocialLinksForm,
    UpdateUserProfile,
    InstructorEditProfile,
)
from .models import Instructor, SocialLinks, Student, User
from .signals import user_signed_up
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied


@login_required
def select_role(request):
    """
    - this function is run when the user is sign-in with social authetication account like google
    - after user finshed the sign-in proccess this function it will run to get the user role from the user
    - and it will send him to the signal to create profile depended on the role of the user choice
    """
    if request.method == "POST":
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]
            social_account = request.user.socialaccount_set.first()
            extra_data = social_account.extra_data if social_account else {}
            signup_data = {
                "role": role,
            }

            user_signed_up.send(
                sender=request.user.__class__,
                user=request.user,
                signup_data=signup_data,
            )

            return redirect("course:index")
    else:
        form = RoleSelectionForm()
    context = {"form": form}
    return render(request, "account/select_role.html", context)


class CustomPasswordChangeView(PasswordChangeView):
    """
    override on allauth password change to some success url and success message
    """

    success_url = reverse_lazy("course:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your password has been changed successfully!")
        return response


def user_profile(request, slug, token):
    try:
        user = User.objects.get(slug=slug, token=token)
    except User.DoesNotExist:
        return messages.info(request, "this user is not found.")
    profile = None
    instructor_courses = None

    if user.role == "instructor":
        profile = Instructor.objects.get(user=user)

        instructor_courses = (
            Course.objects.filter(instructor=profile)
            .select_related("instructor", "category")
            .prefetch_related("course_enrollments")
            .order_by("-created_at")
            # .annotate(enroll=Count("course_enrollments", distinct=True))
            # .order_by("-enroll")
        )
    else:
        profile = Student.objects.get(user=user)

    enrollments_courses = Enrollment.objects.filter(user=user).select_related(
        "course", "user"
    )
    context = {
        "profile": profile,
        "user": user,
        "profile_type": user.role,
        "instructor_courses": instructor_courses,
        "enrollments_courses": (enrollments_courses if enrollments_courses else None),
    }
    return render(request, "account/user_profile.html", context)


@login_required
def edit_profile(request, slug, role, token):
    # get the profile by looping through models and if founded it will break the loop
    user = get_object_or_404(User, slug=slug, role=role, token=token)

    if request.user != user:
        raise PermissionDenied("You can only edit your own profile.")

    instructor = None
    instructor_form = None

    if user.role == "instructor":

        instructor = Instructor.objects.get(user=user)
        # check the request method and implement edit profile proccess

    if request.method == "POST":
        form = UpdateUserProfile(request.POST, request.FILES, instance=user)
        if instructor:
            instructor_form = InstructorEditProfile(request.POST, instance=instructor)

        if form.is_valid():
            form.save()
            if instructor_form and instructor_form.is_valid():
                instructor_form.save()
            messages.success(request, "Profile Is Updated Successfully.")
            return redirect(user.get_absolute_url())
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UpdateUserProfile(instance=user)
        if instructor:
            instructor_form = InstructorEditProfile(instance=instructor)

    context = {"form": form, "profile": user, "instructor_form": instructor_form}
    return render(request, "account/edit_user_profile.html", context)


def delete_profile(request, slug, role, token):
    if request.method == "POST":
        request.user.delete()
        messages.success(request, "Profile is Deleted Successfully.")
        return redirect("course:index")

    return render(request, "account/delete_profile.html")


def public_instructor_profile(request, slug, token):
    try:
        instructor = Instructor.objects.get(user__slug=slug, user__token=token)
    except Instructor.DoesNotExist:
        return redirect("course:home")
    instructor_courses = Course.objects.filter(instructor=instructor).order_by(
        "-created_at"
    )
    context = {"instructor": instructor, "instructor_courses": instructor_courses}
    return render(request, "account/user_public_profile.html", context)


@require_POST
def follow_instructor(request):
    token = request.POST.get("token")
    if not request.user.is_authenticated:
        messages.info(request, "You must be logged in to follow an instructor.")
        return redirect("account_login")
    instructor = Instructor.objects.get(user__token=token)
    if not instructor.followers.filter(id=request.user.id).exists():
        instructor.followers.add(request.user)
        return JsonResponse({"action": "added"})
    else:
        instructor.followers.remove(request.user)
        return JsonResponse({"action": "removed"})


@login_required
def instructor_top_courses(request):
    top_courses = None
    if request.user.instructor:
        top_courses = (
            Course.objects.filter(instructor=request.user.instructor, is_puplished=True)
            .annotate(enroll=Count("course_enrollments"))
            .order_by("-enroll")[:5]
        )
    context = {"top_courses": top_courses}
    return render(request, "course_pages/instructor_top_courses.html", context)


def instructor_courses(request):
    courses = Course.objects.filter(instructor=request.user.instructor)
    context = {"courses": courses}
    return render(request, "course_pages/instructor_courses.html", context)


class CreateLink(CreateView):
    model = SocialLinks
    template_name = "account/create_link.html"
    form_class = SocialLinksForm

    def form_valid(self, form):

        instructor = self.request.user.instructor
        if instructor:
            form.instance.instructor = instructor
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "members:user_profile",
            args=[
                self.object.instructor.user.slug,
                self.object.instructor.user.token,
            ],
        )


class UpdateLink(UpdateView):
    model = SocialLinks
    template_name = "account/update_link.html"
    form_class = SocialLinksForm

    slug_field = "link_name"
    slug_url_kwarg = "name"

    def get_success_url(self):
        return reverse_lazy(
            "members:user_profile",
            args=[
                self.object.instructor.user.slug,
                self.object.instructor.user.token,
            ],
        )


class DeleteLink(DeleteView):
    model = SocialLinks
    template_name = "account/delete_link.html"
    slug_field = "link_name"
    slug_url_kwarg = "name"

    def get_success_url(self):
        return reverse_lazy(
            "members:user_profile",
            args=[
                self.object.instructor.user.slug,
                self.object.instructor.user.token,
            ],
        )
