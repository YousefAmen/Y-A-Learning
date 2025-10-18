from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
    BaseUserSerializer,
    InstructorSerializer,
    StudentSerializer,
    SocialLinkSerializer,
)
from rest_framework import status

from ..models import Instructor, Student, User, SocialLinks


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    serializer = None
    profile = None
    user = User.objects.get(email=request.user.email)
    try:
        if user.role == "instructor":
            profile = Instructor.objects.get(slug=user.slug, token=user.token)
            serializer = InstructorSerializer(profile)
        elif user.role == "student":
            profile = Student.objects.get(slug=user.slug, token=user.token)

            serializer = StudentSerializer(profile)
        else:
            return Response(
                {"error": "No Profile Found."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as ex:
        return Response({"error": str(ex)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def edit_user_profile(request):

    profile = None
    user = User.objects.get(email=request.user.email)
    try:
        profile = Instructor.objects.get(slug=user.slug, token=user.token)
    except Instructor.DoesNotExist:
        try:
            profile = Student.objects.get(slug=user.slug, token=user.token)
        except Student.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

    if profile.role == "student":
        serializer = StudentSerializer(instance=profile, data=request.data)

    elif profile.role == "instructor":
        serializer = InstructorSerializer(instance=profile, data=request.data)
    else:
        return Response(
            {"message": "Profile Is Not Found."}, status=status.HTTP_400_BAD_REQUEST
        )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Updated Successfully.", "data": serializer.data},
            status=status.HTTP_200_OK,
        )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user_profile(request):
    profile = None
    user = User.objects.get(email=request.user.email)
    try:
        profile = Instructor.objects.get(slug=user.slug, token=user.token)
    except Instructor.DoesNotExist:
        try:
            profile = Student.objects.get(slug=user.slug, token=user.token)
        except Student.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)
    request.user.delete()
    return Response(
        {
            "message": f"Your Profile Is Deleted Successfully {profile.first_name} {profile.last_name}"
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def instructor_links(request):
    links = SocialLinks.objects.filter(instructor=request.user)
    serializer = SocialLinkSerializer(links, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_social_links(request):
    serializer = SocialLinkSerializer(data=request.data)
    if request.user.role == "instructor":
        if serializer.is_valid():

            serializer.save(instructor=request.user.instructor)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            {"message": "Only Instructors can add social links"},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_social_links(request, slug):
    try:
        link = SocialLinks.objects.get(slug=slug)
    except SocialLinks.DoesNotExist as er:
        return Response(
            {"error": "Social link not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = SocialLinkSerializer(data=request.data, instance=link, partial=True)
    if request.user.role == "instructor":
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(
            {"message": "Only Instructors can add social links"},
            status=status.HTTP_403_FORBIDDEN,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_social_links(request, slug):

    if request.user.role != "instructor":

        return Response(
            {"message": "Only Instructors can add social links"},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        link = SocialLinks.objects.get(slug=slug, instructor=request.user)
    except SocialLinks.DoesNotExist as er:
        return Response(
            {"error": "Social link not found"}, status=status.HTTP_404_NOT_FOUND
        )

    link_name = link.link_name
    link.delete()
    return Response(
        {"message": f"This '{link_name}' Link Is Delete Successfully."},
        status=status.HTTP_200_OK,
    )
