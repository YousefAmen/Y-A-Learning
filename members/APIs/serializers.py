from rest_framework import serializers
from ..models import User, Student, Instructor, SocialLinks
from djoser.serializers import UserCreateSerializer, UserSerializer
from allauth.account.models import EmailAddress
from course.APIs.serializers import EnrollmentsSerializer, CourseSerializer


class BaseUserSerializer(serializers.ModelSerializer):
    enrollments = EnrollmentsSerializer(
        source="student_enrollments", read_only=True, many=True
    )

    class Meta:
        model = User
        fields = [
            "slug",
            "token",
            "first_name",
            "last_name",
            "email",
            "role",
            "bio",
            "gender",
            "profile_pic",
            "phone",
            "country",
            "birth_date",
            "created_at",
            "updated_at",
            "enrollments",
        ]
        read_only_fields = ["created_at", "slug", "updated_at", "token"]


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLinks
        fields = ["link_name", "link"]


class InstructorSerializer(BaseUserSerializer):
    links = SocialLinkSerializer(source="instructor_links", read_only=True, many=True)

    courses = CourseSerializer(source="instructor_courses", many=True)

    class Meta:
        model = Instructor
        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
            "profile_pic",
            "gender",
            "phone",
            "country",
            "links",
            "birth_date",
            "created_at",
            "updated_at",
            "courses",
        ]


class StudentSerializer(BaseUserSerializer):
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "email",
            "role",
            "profile_pic",
            "gender",
            "phone",
            "country",
            "birth_date",
            "created_at",
            "updated_at",
        ]


class CustomUserCreateSerializer(UserCreateSerializer):

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "role",
            "gender",
            "birth_date",
            "country",
            "password",
        )

    def create(self, validated_data):

        role = validated_data.pop("role")
        email = validated_data.pop("email")
        password = validated_data.pop("password")

        if role == User.Role.INSTRUCTOR:

            user = Instructor.objects.create(email=email, role=role, **validated_data)
        else:
            user = Student.objects.create(email=email, role=role, **validated_data)
        user.set_password(password)

        user.save()
        # also creating a email adddress object when the user is sign in with djoser

        # EmailAddress.objects.create(
        #     user=user, email=user.email, primary=True, verified=True
        # )

        return user
