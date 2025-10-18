from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import CartItem, Cart
from .serializers import CartSerializer, CartItemSerializer
from course.models import Course, Enrollment
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_cart(request):
    cart = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_cart_item(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    course_token = request.data.get("course_token")
    if not course_token:
        raise ValidationError({"course_token": "This field is required."})

    try:

        course = Course.objects.get(token=course_token, is_puplished=True)
    except Course.DoesNotExist:
        raise NotFound("Course Not Found .")
    if Enrollment.objects.filter(course=course, user=request.user).exists():
        raise ValidationError("This Course Is Already In Your Enrolled This Course.")
    cart_item, created = CartItem.objects.get_or_create(course=course, cart=cart)

    if not created:
        raise ValidationError(f"'{course.title}' is already in your cart.")
    cart = Cart.objects.get(pk=cart.pk)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_cart_item(request):
    course_token = request.data.get("course_token")
    if not course_token:
        raise ValidationError({"course_token": "This field is required."})

    course = Course.objects.get(token=course_token)
    cart = CartItem.objects.get(course=course, cart__user=request.user)
    course_title = course.title
    cart.delete()
    return Response(
        {"message": f"Removed {course_title} Successfully."},
        status=status.HTTP_204_NO_CONTENT,
    )
