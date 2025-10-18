from rest_framework.permissions import BasePermission


class IsCourseOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        message = "You don't have permission to access this course."
        return obj.instructor == request.user.instructor


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "instructor")


class IsModuleOrLearningOutcomeOnwer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.course.instructor == request.user.instructor


class IsLessonOnwer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.module.course.instructor == request.user.instructor


class IsCourseEnroll(BasePermission):
    message = "You must enroll in this course."

    def has_object_permission(self, request, view, obj):
        return obj.course_enrollments.filter(user=request.user).exists()


class IsReviewOnwer(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsContactMessageOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
