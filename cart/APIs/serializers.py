from rest_framework import serializers
from ..models import Cart, CartItem
from course.APIs.serializers import CourseSerializer
from course.models import Course, Enrollment


class CartItemSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "course", "added_at", "price"]
        read_only_fields = ["id", "added_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "total_price",
            "cart_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
