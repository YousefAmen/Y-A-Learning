from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from ..models import (
    Category,
    Contact,
    Course,
    Enrollment,
    Module,
    LearningOutcomes,
    Review,
    Lesson,
)
from .serializers import (
    CategorySerializer,
    ContactSerializer,
    CourseSerializer,
    ModuelSerializer,
    EnrollmentsSerializer,
    LearningOutcomesSerializer,
    LessonSerializer,
    ReviewSerializer,
)
from ..filters import CourseFilter
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .permissions import (
    IsContactMessageOwner,
    IsCourseEnroll,
    IsCourseOwner,
    IsInstructor,
    IsLessonOnwer,
    IsModuleOrLearningOutcomeOnwer,
    IsReviewOnwer,
)
from rest_framework import viewsets
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)

from django.views.decorators.csrf import csrf_exempt
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from rest_framework.pagination import PageNumberPagination

"""
- here i will make the same code with there patterns to show my skills and what i can do with djangorestframework 
     - API View
     - Viewsets
     - Function Views

"""


"""
- first pattern :Functions
- which is the default but is not used in all time it only used for complex logic 
"""


def get_course_or_module_object(
    slug, instructor=None, token=None, object_type="course"
):
    """
    - slug expected - > Course slug | token expected -> Course Token | and instructor it should the instructor is owned this course
    - this two params is used to get the course and linked it with created modules
    - also it working to get the modules / module
    """
    if object_type == "course":
        try:
            if instructor:
                course = Course.objects.get(
                    slug=slug, token=token, instructor=instructor
                )
                if course.instructor != instructor:
                    raise PermissionDenied(
                        "You don't have permission to access this course."
                    )
                return course
            else:
                course = Course.objects.get(slug=slug, token=token)
                return course
        except:
            raise NotFound("this course is not found.")
    elif object_type == "module":
        if token and not instructor:
            try:
                modules = Module.objects.filter(
                    course__slug=slug,
                    course__token=token,
                )

                if not modules.exists():
                    raise NotFound("No modules found for this course.")

                return modules
            except Module.DoesNotExist:
                raise NotFound("this module is not found.")
        else:
            module = Module.objects.get(slug=slug)

        if module.course.instructor != instructor:
            raise PermissionDenied("you don't have permission to preform this action.")
        return module

    else:
        raise ValidationError("Invalid object_type. Must be 'course' or 'module'.")


def get_learning_outcome_object(instructor, slug):

    try:
        outcome = LearningOutcomes.objects.get(slug=slug, course__instructor=instructor)

        return outcome
    except LearningOutcomes.DoesNotExist:
        raise NotFound("this outcome is not found.")


def get_lesson_object(instructor, token):
    try:
        lesson = Lesson.objects.get(token=token)
        if lesson.module.course.instructor != instructor:
            raise PermissionDenied("you don't have permission to preform this action.")
        return lesson
    except Lesson.DoesNotExist:
        raise NotFound("this lesson is not found.")


# start working on courses


@api_view(["GET"])
@permission_classes([AllowAny])
def courses_list(request):
    courses = (
        Course.objects.all()
        .select_related("instructor", "category")
        .prefetch_related(
            "tags",
            "course_outcomes",
            "course_reviews",
            "modules",
            "modules__lessons",
            "course_enrollments",
        )
        .annotate(enroll=Count("course_enrollments"), rate=Count("course_reviews"))
        .order_by("-enroll", "-rate")
    )

    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def course_detail(request, slug, token):
    course = Course.objects.get(is_puplished=True, slug=slug, token=token)
    serializer = CourseSerializer(course)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsInstructor])
def create_course(request):
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(instructor=request.user.instructor)
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated, IsCourseOwner])
def update_course(request, slug, token):
    instructor = request.user.instructor
    course, error = get_course_or_module_object(
        instructor=instructor,
        slug=slug,
        token=token,
    )
    if error:
        return error
    serializer = CourseSerializer(data=request.data, instance=course, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsCourseOwner])
def delete_course(request, slug, token):

    instructor = request.user.instructor
    course, error = get_course_or_module_object(
        instructor=instructor,
        slug=slug,
        token=token,
    )
    if error:
        return error
    course.delete()
    return Response(
        {"message": "deleted successfully."}, status=status.HTTP_204_NO_CONTENT
    )


# start working on modules


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def modules_list(request, slug, token):
    instructor = request.user.instructor
    # here you get the course modules so we filter by course token and slug to get the all moduels related to this course
    modules = get_course_or_module_object(slug=slug, token=token, object_type="module")

    serializer = ModuelSerializer(modules, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsInstructor])
def draft_modules(request, slug, token):
    instructor = request.user.instructor
    # here you get the course modules so we filter by course token and slug to get the all moduels related to this course
    modules = get_course_or_module_object(
        instructor=instructor, slug=slug, token=token, object_type="module"
    )

    serializer = ModuelSerializer(modules, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsInstructor])
def create_modules(request, slug, token):

    instructor = request.user.instructor
    course = get_course_or_module_object(slug=slug, token=token, instructor=instructor)

    serializer = ModuelSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(course=course)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated, IsInstructor])
def update_modules(request, slug):

    instructor = request.user.instructor
    module = get_course_or_module_object(
        instructor=instructor, slug=slug, object_type="module"
    )

    serializer = ModuelSerializer(data=request.data, instance=module, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsInstructor])
def delete_modules(request, slug):

    instructor = request.user.instructor
    module = get_course_or_module_object(
        instructor=instructor, slug=slug, object_type="module"
    )

    module.delete()
    return Response(
        {"message": "Module deleted successfully."}, status=status.HTTP_200_OK
    )


# start working on modules


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsInstructor])
def course_learning_outcome(request, slug, token):
    """
    - param:
        - slug : expected course slug
        - toekn : expected course token
    """
    instructor = request.user.instructor
    course = get_course_or_module_object(instructor=instructor, slug=slug, token=token)
    learning_outcomes = LearningOutcomes.objects.filter(course=course)
    serializer = LearningOutcomesSerializer(learning_outcomes, many=True)

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsInstructor])
def create_learning_outcome(request, slug, token):
    """
    - param:
        - slug : expected course slug
        - toekn : expected course token
    """
    instructor = request.user.instructor
    course = get_course_or_module_object(instructor=instructor, slug=slug, token=token)
    serializer = LearningOutcomesSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(course=course)
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated, IsInstructor])
def update_learning_outcomes(request, slug):

    instructor = request.user.instructor
    learning_outcome = get_learning_outcome_object(instructor=instructor, slug=slug)

    serializer = LearningOutcomesSerializer(
        data=request.data, instance=learning_outcome, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsInstructor])
@csrf_exempt
def delete_learning_outcomes(request, slug):

    instructor = request.user.instructor
    learning_outcome = get_learning_outcome_object(instructor=instructor, slug=slug)
    learning_outcome.delete()

    return Response(
        {"message": "Learning outcome deleted successfully."},
        status=status.HTTP_204_NO_CONTENT,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsInstructor])
def adding_lessons(request, slug):
    """
    - param :
        - slug expected module slug
    """
    module = get_course_or_module_object(
        slug=slug, instructor=request.user.instructor, object_type="module"
    )
    serializer = LessonSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(module=module)
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def module_lessons(request, slug):
    module = get_course_or_module_object(
        slug=slug, instructor=request.user.instructor, object_type="module"
    )
    lessons = Lesson.objects.filter(module=module)
    serializer = LessonSerializer(lessons, many=True)
    return Response(serializer.data)


@api_view(["PUT", "PATHC"])
@permission_classes([IsAuthenticated, IsInstructor])
def update_lesson(request, lesson_token):
    instructor = request.user.instructor
    lesson = get_lesson_object(instructor=instructor, token=lesson_token)
    serializer = LessonSerializer(data=request.data, instance=lesson, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated, IsInstructor])
def delete_lesson(request, lesson_token):
    instructor = request.user.instructor
    lesson = get_lesson_object(instructor=instructor, token=lesson_token)

    lesson.delete()
    return Response(
        {"message": "deleted successfully."}, status=status.HTTP_204_NO_CONTENT
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review(request, course_slug, course_token):
    course = get_course_or_module_object(slug=course_slug, token=course_token)

    print(f"--------{course.course_enrollments.count()}-----------")
    if course.course_enrollments.filter(user=request.user).exists():
        print("success")
        serializer = ReviewSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(course=course, user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        raise PermissionDenied("you should enroll this course to can leave comment.")


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_review(request, review_slug):
    user = request.user
    try:
        review = Review.objects.get(user=user, slug=review_slug)
    except Review.DoesNotExist:
        raise NotFound("this comment is not found.")
    serializer = ReviewSerializer(data=request.data, instance=review, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_review(request, review_slug):
    user = request.user
    try:
        review = Review.objects.get(user=user, slug=review_slug)
    except Review.DoesNotExist:
        raise NotFound("this comment is not found.")
    review.delete()
    return Response(
        {"message": "deleted successfully."}, status=status.HTTP_204_NO_CONTENT
    )


"""
- secound pattern : generic API Endpoints
"""


class CoursesList(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filterset_class = CourseFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]
    filterset_class = CourseFilter
    search_fields = ["title", "subtitle", "description"]
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5
    pagination_class.page_size_query_param = "page_size"
    pagination_class.max_page_size = 10

    def get_queryset(self):
        return (
            Course.objects.select_related("category", "instructor")
            .prefetch_related(
                "tags",
                "course_outcomes",
                "course_reviews",
                "modules",
                "modules__lessons",
                "course_enrollments",
            )
            .annotate(
                enroll=Count("course_enrollments"), rate=Count("course_reviews__rate")
            )
            .order_by("-enroll", "-rate")
        )


# makeing class is get the the course object and let the two endpoints update and delete to inhireting from it to prevent duplicateing code as we can
class GetCourseObject:
    def get_object(self):
        """
        - override on get object mthod to get the course object by the slug and token
            becuse the defualt behaviour is allow to use just get object depeneded on
            what is in look_up fild if you overrid on it
        """
        try:
            slug = self.kwargs["slug"]
            token = self.kwargs["token"]
            course = Course.objects.get(slug=slug, token=token)
            # call check permission to check the permissions depended on what is in permission_classes on this object
            self.check_object_permissions(self.request, course)
            return course
        except Course.DoesNotExist:
            raise NotFound("Course not found with the provided slug and token")


class CreateCourseView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructor]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user.instructor)


class UpdateCourseView(GetCourseObject, generics.RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsCourseOwner]


class DeleteCourseView(GetCourseObject, generics.RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsCourseOwner]


class InstructorCourseView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, "instructor"):
            return (
                Course.objects.filter(instructor=self.request.user.instructor)
                .annotate(
                    enroll=Count("course_enrollments"),
                    rating=Count("course_reviews__rate"),
                )
                .order_by("-enroll", "-rating", "-created_at")
            )


class AllCourseLearningOutcomes(generics.ListAPIView):
    queryset = LearningOutcomes.objects.all()
    serializer_class = LearningOutcomesSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["description", "course__title"]
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        try:
            slug = self.kwargs["slug"]
            token = self.kwargs["token"]
            course = Course.objects.get(slug=slug, token=token)
            if course.instructor != self.request.user.instructor:
                raise PermissionDenied(
                    "You don't have permission to access this course."
                )

            return LearningOutcomes.objects.filter(course=course)
        except Course.DoesNotExist:
            raise NotFound("Course not found with the provided slug and token")


class CreateLearningOutcome(GetCourseObject, generics.ListCreateAPIView):
    queryset = LearningOutcomes.objects.all()
    serializer_class = LearningOutcomesSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsCourseOwner]

    def get_queryset(self):
        return LearningOutcomes.objects.filter(module=self.kwargs["slug"])


class UpdateLearningOutcome(generics.RetrieveUpdateAPIView):
    queryset = LearningOutcomes.objects.all()
    serializer_class = LearningOutcomesSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsModuleOrLearningOutcomeOnwer]
    lookup_field = "slug"


class DeleteLearningOutcome(generics.RetrieveDestroyAPIView):
    queryset = LearningOutcomes.objects.all()
    serializer_class = LearningOutcomesSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsModuleOrLearningOutcomeOnwer]
    lookup_field = "slug"


class AllCourseModules(generics.ListAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuelSerializer
    permission_classes = [IsAuthenticated, IsInstructor]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "description"]
    ordering_fields = ["is_published", "created_at", "updated_at"]
    ordering = ["created_at"]

    def get_queryset(self):
        try:
            slug = self.kwargs["slug"]
            token = self.kwargs["token"]
            course = Course.objects.get(slug=slug, token=token)
            if course.instructor != self.request.user.instructor:
                raise PermissionDenied(
                    "You don't have permission to access this course."
                )

            return Module.objects.filter(course=course)
        except Course.DoesNotExist:
            raise NotFound("Course not found with the provided slug and token")


class CreateModuleView(GetCourseObject, generics.CreateAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuelSerializer

    def perform_create(self, serializer):
        serializer.save(course=self.get_object())


class UpdateModuleView(generics.RetrieveUpdateAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuelSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsModuleOrLearningOutcomeOnwer]
    lookup_field = "slug"


class DeleteModuleView(generics.RetrieveDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuelSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsModuleOrLearningOutcomeOnwer]
    lookup_field = "slug"


class AllCourseLessons(generics.ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsCourseOwner]
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "module__description"]
    ordering_fields = ["is_preview", "duration", "added_at"]
    ordering = ["added_at"]

    def get_object(self):

        course = Course.objects.get(
            slug=self.kwargs["course_slug"], token=self.kwargs["course_token"]
        )
        modules = Module.objects.filter(
            course__slug=course.slug, course__token=course.token
        )
        # here i used the IsCourseOnwer instaed IsModuleOLearningOnwer becuse i cannot useing permission on querysat
        self.check_object_permissions(self.request, course)
        return modules

    def get_queryset(self):
        modules = self.get_object()
        return Lesson.objects.filter(module__in=modules)


class AddingLessonView(generics.CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsModuleOrLearningOutcomeOnwer]

    def get_object(self):
        try:
            slug = self.kwargs["module_slug"]

            module = Module.objects.get(slug=slug)
            self.check_object_permissions(self.request, module)
            return module
        except Module.DoesNotExist:
            raise NotFound("this module is not found.")

    def perform_create(self, serializer):
        serializer.save(module=self.get_object())


class UpdateLessonView(generics.RetrieveUpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsLessonOnwer]
    lookup_field = "token"


class DeleteLessonView(generics.RetrieveDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructor, IsLessonOnwer]
    lookup_field = "token"


class CreateReviewApiView(GetCourseObject, generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsCourseEnroll]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, course=self.get_object())


class UpateReviewApiView(generics.RetrieveUpdateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOnwer]
    lookup_field = "slug"


class DeleteReviewApiView(generics.RetrieveDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOnwer]
    lookup_field = "slug"


# class CreateCategoryView(generics.CreateAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [IsAdminUser]


# class CategoriesListView(generics.ListAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [IsAdminUser]

#     filter_backends = [
#         filters.SearchFilter,
#     ]
#     search_fields = ["name"]


# class UpdateCategoryView(generics.RetrieveUpdateAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [IsAdminUser]
#     lookup_field = "slug"


# class CategoriesListView(generics.RetrieveDestroyAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [IsAdminUser]
#     lookup_field = "slug"


# class CreateContactView(generics.CreateAPIView):
#     queryset = Contact.objects.all()
#     serializer_class = ContactSerializer
#     permission_classes = [IsAuthenticated]


# class UserContactsView(generics.ListAPIView):
#     queryset = Contact.objects.all()
#     serializer_class = ContactSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return Contact.objects.filter(user=self.request.user)


# class UpdateContactView(generics.RetrieveUpdateAPIView):
#     queryset = Contact.objects.all()
#     serializer_class = ContactSerializer
#     permission_classes = [IsAuthenticated, IsContactMessageOwner]
#     lookup_field = "token"


# class DeleteContactView(generics.RetrieveDestroyAPIView):
#     queryset = Contact.objects.all()
#     serializer_class = ContactSerializer
#     permission_classes = [IsAuthenticated, IsContactMessageOwner]
#     lookup_field = "token"


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]


class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsContactMessageOwner]
    lookup_field = "token"

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Contact.objects.filter(user=self.request.user)
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
