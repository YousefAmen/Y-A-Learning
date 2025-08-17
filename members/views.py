from allauth.account.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from course.models import Course, Enrollment

from .forms import RoleSelectionForm, SocialLinksForm, UpdateUserProfile
from .models import Instructor, Profile, SocialLinks, Student
from .signals import user_signed_up
from django.db.models import Count


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
                "first_name": extra_data.get("given_name", "John"),
                "last_name": extra_data.get("family_name", "Doe"),
                "gender": extra_data.get("gender", "male"),
                "birth_date": extra_data.get("brithdate", "2000-01-01"),
                "country": extra_data.get("country", ""),
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
    profile_models = [Instructor, Student]
    for model in profile_models:
        profile = model.objects.filter(slug=slug, token=token).first()
        if profile:
            break
    else:
        messages.info(request, "This Profile Is Not Exsits!.")
        return redirect("course:index")
    instructor_courses = None
    student_enrollments_courses = None

    if profile.role == "instructor":
        instructor_courses = (
            Course.objects.filter(instructor=profile)
            .annotate(enroll=Count("course_enrollments", distinct=True))
            .order_by("-enroll")
        )
    if profile.role == "student":
        student_enrollments_courses = Enrollment.objects.filter(user=profile.user)

    context = {
        "profile": profile,
        "instructor_courses": instructor_courses,
        "student_enrollments": (
            student_enrollments_courses if student_enrollments_courses else None
        ),
    }
    return render(request, "account/user_profile.html", context)


def edit_profile(request, slug, role, token):
    # get the profile by looping through models and if founded it will break the loop
    profile_models = [Instructor, Student]
    for model in profile_models:
        profile = model.objects.filter(slug=slug, role=role, token=token).first()
        if profile:
            break

    # check the request method and implement edit profile proccess
    if request.method == "POST":
        form = UpdateUserProfile(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Is Updated Successfully.")
            return redirect(profile.get_absolute_url())
        else:
            messages.error(request, "Error")
    else:
        form = UpdateUserProfile(instance=profile)
    context = {"form": form, "profile": profile}
    return render(request, "account/edit_user_profile.html", context)


def delete_profile(request, slug, role, token):
    if request.method == "POST":
        request.user.delete()
        messages.success(request, "Profile is Deleted Successfully.")
        return redirect("course:index")

    return render(request, "account/delete_profile.html")


class UserPublicProfile(ListView):
    model = Course
    template_name = "account/user_public_profile.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.instructor = Instructor.objects.get(
                slug=self.kwargs["slug"], token=self.kwargs["token"]
            )
            return super().dispatch(request, *args, **kwargs)
        except Instructor.DoesNotExist:
            messages.info(self.request, "This instructor profile does not exist.")
            return reverse_lazy(
                "members:user_public_profile",
                args=[
                    self.kwargs["slug"],
                    self.kwargs["token"],
                ],
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instructor_courses = Course.objects.filter(instructor=self.instructor)
        context["instructor"] = self.instructor
        context["instructor_courses"] = instructor_courses
        return context


def follow_instructor(request, slug, token):
    instructor = Instructor.objects.get(slug=slug, token=token)
    if instructor.followers.filter(id=request.user.id):
        instructor.followers.remove(request.user)
    else:
        instructor.followers.add(request.user)


def love_course(request):
    pass


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
                self.object.instructor.slug,
                self.object.instructor.token,
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
                self.object.instructor.slug,
                self.object.instructor.token,
            ],
        )


class DeleteLink(DeleteView):
    model = SocialLinks
    template_name = "account/delete_link.html"
    slug_field = "link_name"
    slug_url_kwarg = "name"

    def get_success_url(self):
        instructor = self.object.instructor

        return reverse_lazy(
            "members:user_profile",
            args=[
                instructor.slug,
                instructor.token,
            ],
        )
