from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from members.models import Instructor, Student

from .forms import (
    AddCourseForms,
    AddLessonForm,
    ContactForm,
    CreateLearningOutcomesForm,
    CreateModuleForm,
    ReviewForm,
    SearchForm,
)
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
from taggit.models import Tag


class Index(TemplateView):
    template_name = "course_pages/index.html"


class About(TemplateView):
    template_name = "about.html"


class CreateCourse(PermissionRequiredMixin, CreateView):
    model = Course
    form_class = AddCourseForms
    template_name = "course_pages/add_course.html"
    permission_required = "course.add_course"

    def form_valid(self, form):
        user = self.request.user

        form.instance.user = user
        form.instance.instructor = user.instructor
        messages.success(self.request, "Your course has been uploaded successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "course:create-learning-objectives",
            args=[
                self.object.slug,
                self.object.token,
            ],
        )


class UpdateCourse(PermissionRequiredMixin, UpdateView):
    model = Course
    form_class = AddCourseForms
    template_name = "course_pages/update_course.html"
    success_url = reverse_lazy("course:index")
    permission_required = "course.change_course"


class DeleteCourse(PermissionRequiredMixin, DeleteView):
    model = Course
    template_name = "course_pages/delete_course.html"
    success_url = reverse_lazy("course:index")
    permission_required = "course.delete_course"


class CreateLearningObjectives(CreateView):
    model = LearningOutcomes
    template_name = "course_pages/create_learning_outcomes.html"
    form_class = CreateLearningOutcomesForm

    def get_course(self):
        return Course.objects.get(slug=self.kwargs["slug"], token=self.kwargs["token"])

    def form_valid(self, form):
        course = self.get_course()
        form.instance.course = course
        messages.success(self.request, "Add Successfully.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_course()
        course_outcomes = LearningOutcomes.objects.filter(course=course)
        context["course"] = course
        context["course_outcomes"] = course_outcomes
        return context

    def get_success_url(self):
        course = self.get_course()
        return reverse_lazy(
            "course:create-learning-objectives",
            args=[
                course.slug,
                course.token,
            ],
        )


class EditLearningObjectives(UpdateView):
    model = LearningOutcomes
    template_name = "course_pages/edit_learning_outcomes.html"
    form_class = CreateLearningOutcomesForm
    context_object_name = "objective"

    def form_valid(self, form):
        outcome = self.get_object()
        if not self.request.user.instructor == outcome.course.instructor:
            messages.info(
                self.request, "You don't have premission to edit this objective"
            )
        return super().form_valid(form)

    def get_success_url(self):
        objective = self.get_object()
        return reverse_lazy(
            "course:create-learning-objectives",
            args=[
                objective.course.slug,
                objective.course.token,
            ],
        )


class DeleteLearningObjectives(DeleteView):
    model = LearningOutcomes
    template_name = "course_pages/delete_learning_outcomes.html"
    context_object_name = "objective"

    def get_success_url(self):
        objective = self.get_object()
        return reverse_lazy(
            "course:create-learning-objectives",
            args=[
                objective.course.slug,
                objective.course.token,
            ],
        )


def most_viewed_courses(request):
    pass


class CreateModule(PermissionRequiredMixin, CreateView):
    model = Module
    template_name = "course_pages/create_module.html"
    form_class = CreateModuleForm
    permission_required = "module.add_module"

    def get_course(self):
        return Course.objects.get(slug=self.kwargs["slug"], token=self.kwargs["token"])

    def form_valid(self, form):
        course = self.get_course()
        form.instance.course = course
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_course()

        course_modules = Module.objects.filter(course=course).order_by("-created_at")

        context["course_modules"] = course_modules
        context["course"] = course

        return context

    def get_success_url(self):
        course = self.get_course()
        messages.success(
            self.request, f"Your {self.object.title } module is created successfully."
        )
        return reverse_lazy(
            "course:create-module",
            args=[
                course.slug,
                course.token,
            ],
        )


class EditModule(PermissionRequiredMixin, UpdateView):
    model = Module
    template_name = "course_pages/edit_module.html"
    form_class = CreateModuleForm
    permission_required = "module.change_module"

    def get_success_url(self):
        course = self.object.course
        return reverse_lazy(
            "course:create-module",
            args=[
                course.slug,
                course.token,
            ],
        )


class DeleteModule(PermissionRequiredMixin, DeleteView):
    model = Module
    template_name = "course_pages/delete_module.html"
    permission_required = "module.delete_module"

    def get_success_url(self):
        course = self.object.course
        return reverse_lazy("course:create-module", args=[course.slug, course.token])


class AddLessonView(CreateView):
    model = Lesson
    template_name = "course_pages/add_lesson.html"
    form_class = AddLessonForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        module = Module.objects.get(slug=self.kwargs["slug"])
        context["module"] = module
        return context

    def form_valid(self, form):
        module = Module.objects.get(slug=self.kwargs["slug"])
        form.instance.module = module
        messages.success(
            self.request,
            f"The lesson is created successfully and is add in {module.title}",
        )
        return super().form_valid(form)

    def get_success_url(self):
        lesson = self.object
        return reverse_lazy(
            "course:create-module",
            args=[
                lesson.module.course.slug,
                lesson.module.course.token,
            ],
        )


class EditLesson(PermissionRequiredMixin, UpdateView):
    model = Lesson
    template_name = "course_pages/edit_lesson.html"
    form_class = AddLessonForm
    permission_required = "lesson.add_lesson"

    def get_success_url(self):
        lesson = self.object
        return reverse_lazy(
            "course:create-module",
            args=[
                lesson.module.course.slug,
                lesson.module.course.token,
            ],
        )


class DeleteLesson(PermissionRequiredMixin, DeleteView):
    model = Lesson
    template_name = "course_pages/delete_lesson.html"
    permission_required = "lesson.delete_lesson"

    def get_success_url(self):
        lesson = self.object
        return reverse_lazy(
            "course:create-module",
            args=[
                lesson.module.course.slug,
                lesson.module.course.token,
            ],
        )


class CoursesList(ListView):
    model = Course
    template_name = "course_pages/courses.html"
    ordering = ["-created_at"]
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(is_puplished=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        context["categories"] = categories
        return context


class CourseDetail(DetailView):
    model = Course
    template_name = "course_pages/course_detail.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        if self.request.user.is_authenticated:
            if course.course_enrollments.filter(user=self.request.user).exists():
                context["is_enrolled"] = True
            else:
                context["is_enrolled"] = False
        return context


class LessonDetail(DetailView):
    model = Lesson
    template_name = "course/lesson_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["add_views"] = self.add_views()
        return context

    def add_views(self):

        course = self.get_object()
        if self.request.user.is_authenticated:
            if not course.is_free:
                if (
                    self.request.user.student
                    and course.course_enrollments.filter(
                        student=self.request.user.student
                    ).exists()
                ):

                    course.views += 1
                    course.save()
                else:

                    return redirect(
                        "course:course_detail", kwargs=[course.slug, course.token]
                    )
            else:
                course.views += 1
                course.save()


def fetch_courses_by_tag(request, tag):

    courses = Course.objects.filter(tags__name=tag).order_by("-created_at")
    context = {"courses": courses, "tag": tag}
    return render(request, "course_pages/fetch_courses_by_tag.html", context)


def fetch_courses_by_category(request, slug):

    courses = Course.objects.filter(category__slug=slug).order_by("-created_at")
    category = Category.objects.get(slug=slug)
    if "category_views" not in request.session:
        request.session["category_views"] = []
    if request.user.id not in request.session["category_views"]:
        category.views += 1
        category.save()
        request.session["category_views"].append(request.user.id)
        request.session.modified = True
    popular_categories = Category.objects.all().order_by("-views")[:5]
    context = {
        "courses": courses,
        "category": category,
        "popular_categories": popular_categories,
    }
    return render(request, "course_pages/fetch_courses_by_category.html", context)


def search(request):
    results = {"instructors": None, "courses": None}
    query = None
    form = SearchForm(request.GET or None)
    selected_levels = request.GET.getlist("level")
    sort = request.GET.get("sort")
    courses = Course.objects.filter(is_puplished=True).order_by("-created_at")

    if "search" in request.GET and form.is_valid():
        query = form.cleaned_data["search"]
        courses = (
            courses.filter(
                Q(title__icontains=query) | Q(description__icontains=query),
                is_puplished=True,
            )
            .order_by("-created_at")
            .distinct()
        )
        instructors = Instructor.objects.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query)
        ).distinct()

        if courses.exists():
            results["courses"] = courses
        if instructors.exists():
            results["instructors"] = instructors

    # level filter
    if selected_levels:
        courses = (
            Course.objects.filter(level__in=selected_levels, is_puplished=True)
            .filter(Q(title__icontains=query) | Q(description__icontains=query))
            .annotate(enroll_count=Count("course_enrollments"))
            .order_by("-enroll_count")
        )

        results["courses"] = courses
    # recommanded courses
    if sort == "recommended":
        courses = courses.annotate(enroll_counts=Count("course_enrollments")).order_by(
            "-enroll_counts"
        )
    if sort == "newest":
        courses = courses.order_by("-created_at")
    if sort == "popular":

        courses = courses.annotate(
            views_counter=Sum("modules__lessons__views")
        ).order_by("-views_counter")
    if sort == "rating":
        courses = courses.annotate(avg_rating=Avg("reviews__rating")).order_by(
            "-avg_rating"
        )

    results["courses"] = courses

    # sidebar data
    top_enrollments_courses = Course.objects.annotate(
        enrollments_count=Count("course_enrollments")
    ).order_by("-enrollments_count")[:5]
    top_topics = Tag.objects.annotate(popular_topics=Count("course")).order_by(
        "-popular_topics"
    )[:5]
    context = {
        "form": form,
        "query": query,
        "results": results,
        "top_enrollments_courses": top_enrollments_courses,
        "top_topices": top_topics,
    }
    return render(request, "course_pages/search.html", context)


def create_review(request, token):
    try:
        course = Course.objects.get(token=token)
    except Course.DoesNotExist:
        return messages.error(
            request, "Something Happend,Please Try To Adding Review Agine."
        )
    if request.user.is_authenticated:
        form = ReviewForm()
        if request.method == "POST":
            form = ReviewForm(request.POST or None)
            if form.is_valid():
                presave_form = form.save(commit=False)
                presave_form.course = course
                presave_form.user = request.user
                presave_form.save()
                messages.success(request, "Your Review Adding Successfully.")
                return redirect("course:course-detail", course.slug, course.token)
            else:
                return messages.error(
                    request, "Something Wrong Please Try To Adding Agine"
                )
    context = {"form": form, "course": course}
    return render(request, "course_pages/create_review.html", context)


def update_review(request, slug):
    try:
        review = Review.objects.get(slug=slug)
    except Review.DoesNotExist:
        return messages.error(
            request, "Something Happend,Please Try To Update Review Agine."
        )
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review Updated Successfully.")
            return redirect(
                "course:course-detail", review.course.slug, review.course.token
            )
        else:
            return messages.error(request, "Something Wrong Please Try To Adding Agine")
    else:
        form = ReviewForm(instance=review)
        course = review.course
    context = {"form": form, "course": course}
    return render(request, "course_pages/update_review.html", context)


def remove_review(request, slug):
    try:
        review = Review.objects.get(slug=slug)
    except Review.DoesNotExist:
        return messages.error(
            request, "Something Happend,Please Try To Update Review Agine."
        )
    if request.method == "POST":
        review.delete()
        messages.success(request, "Your Review Is Deleted Successfully.")
        return redirect("course:course-detail", review.course.slug, review.course.token)
    context = {"review": review}
    return render(request, "course_pages/remove_review.html", context)


def create_rating(request, token):
    pass


def update_rating(request, token):
    pass


def remove_rating(request, token):
    pass


def create_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Your Message Is Sent Successfully And You Get the Response Soon.",
            )
            return redirect("course:index")
        else:
            messages.info(
                request,
                "Something Wrong,Please Check Your Details And Re-Sent The Message",
            )
            return redirect("course:index")
    else:
        form = ContactForm()
    context = {"form": form}
    return render(request, "course_pages/contact.html", context)


def update_contact(request, token):
    try:
        message = Contact.objects.get(token=token)
    except Contact.DoesNotExist:
        message.error(request, "This Message Is Not Exist Anymore.")
    if request.method == "POST":
        form = ContactForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            messages.success(request, "Message Updated Successfully.")
            return redirect("course:user-contact-message", message.token)
        else:
            messages.info(
                request,
                "Invalid Fill Form,Please Check Your Detail And Re-Sent The Message Agien.",
            )
    else:
        form = ContactForm(instance=message)

    context = {"form": form, "message": message}
    return render(request, "course_pages/update_contact_message.html", context)


def delete_contact(request, token):
    try:
        message = Contact.objects.get(token=token)
    except Contact.DoesNotExist:
        message.error(request, "This Message Is Not Exist Anymore.")
    if request.method == "POST":
        message.delete()
        messages.success(request, "The Message is Deleted Successfully.")
        return redirect("course:user-contact-message", message.token)
    context = {"message": message}
    return render(request, "course_pages/delete_contact.html", context)


def user_contact_messages(request):
    pass
