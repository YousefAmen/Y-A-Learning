from django.db import models
from course.models import Course
from main import settings


class Cart(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart({self.id}) - User({self.user.email})"

    @property
    def total_price(self):
        total = self.items.aggregate(total=sum("course__price"))["total"]
        return total or 0

    def clear(self):
        self.items.all().delete()

    @property
    def cart_count(self):
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "course")

    def __str__(self):
        return f"Orderd '{self.course.title}' by {self.cart.user.email}"

    @property
    def price(self):
        return self.course.price
