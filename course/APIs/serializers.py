from rest_framework import serializers
from members.models import Instructor
from ..models import (
    Category,
    Course,
    Enrollment,
    LearningOutcomes,
    Module,
    Lesson,
    Review,
)
from taggit.serializers import TaggitSerializer, TagListSerializerField
from django.db.models import Count, Avg


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "token",
            "slug",
            "title",
            "video",
            "is_preview",
            "duration",
            "added_at",
        ]


class ModuelSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(read_only=True, many=True)
    lectures = serializers.SerializerMethodField()
    avg_lectures_duration = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            "title",
            "description",
            "is_published",
            "created_at",
            "updated_at",
            "slug",
            "get_total_duration",
            "lessons",
            "lectures",
            "avg_lectures_duration",
        ]

    def get_lectures(self, obj):
        return obj.lessons.count()

    def get_avg_lectures_duration(self, obj):
        return obj.lessons.aggregate(avrage=Avg("duration"))["avrage"]


class LearningOutcomesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningOutcomes
        fields = ["slug", "description", "created_at", "updated_at"]


class CourseSerializer(TaggitSerializer, serializers.ModelSerializer):
    instructor = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    tags = TagListSerializerField()
    stats = serializers.SerializerMethodField()
    modules = ModuelSerializer(read_only=True, many=True)
    learning_outcomes = LearningOutcomesSerializer(
        source="course_outcomes", many=True, read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "token",
            "slug",
            "title",
            "subtitle",
            "description",
            "requirements",
            "image",
            "promo_video",
            "price",
            "discount",
            "level",
            "is_free",
            "created_at",
            "updated_at",
            "published_at",
            "is_puplished",
            "category",
            "tags",
            "stats",
            "get_absolute_url",
            "instructor",
            "modules",
            "learning_outcomes",
        ]

    def get_stats(self, obj):
        return {
            "total_course_duration": obj.total_course_duration,
            "discount_percentage": obj.discount_percentage,
            "avg_rating": obj.avg_rating,
            "enrollments": obj.course_enrollments.count(),
            "sections": obj.modules.count(),
            "reviews": obj.course_reviews.count(),
        }

    def get_instructor(self, obj):
        return {
            "first_name": obj.instructor.first_name,
            "last_name": obj.instructor.last_name,
            "profile_pic": obj.instructor.profile_pic,
            "about": obj.instructor.about,
            "get_total_reviews": obj.instructor.get_total_reviews,
            "get_students_count": obj.instructor.get_students_count,
            "get_avg_instructor_rating": obj.instructor.get_avg_instructor_rating,
        }


class EnrollmentsSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ["token", "course", "enrollment_date"]


class ReviewSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["slug", "rate", "body", "course", "user", "created_at", "updated_at"]

    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email,
            "profile_pic": obj.user.profile_pic,
        }

    def validate_rate(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("rating must be between 0 and 5.")
        return value

    def get_course(sef, obj):
        return {
            "token": obj.course.token,
            "slug": obj.course.slug,
            "title": obj.course.title,
            "subtitle": obj.course.subtitle,
            "level": obj.course.level,
        }


class ContactSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["token", "name", "email", "subject", "message", "user", "created_at"]

    def get_user(self, obj):
        return {
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "email": obj.user.email,
            "profile_pic": obj.user.profile_pic,
        }
