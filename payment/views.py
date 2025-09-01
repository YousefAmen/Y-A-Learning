import uuid
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from main import settings
from django.urls import reverse
from django.views import View
from django.db import transaction

# Import your models
from course.models import Course, Enrollment
from cart.cart import Cart
from paypal.standard.forms import PayPalPaymentsForm


@login_required
def checkout(
    request,
):
    token = request.GET.get("token")
    items = []
    total = 0
    cart = Cart(request)
    if (
        token and len(token) > 0
    ):  # that's mean the user is click on buy now button directly don't comes from the cart
        token = token[0:-1]
        try:
            course = Course.objects.get(token=token)
            items.append(course.token)
        except Course.DoesNotExist:
            messages.error(request, "Course not found.")
            return redirect("courses:course-list")
    else:

        cart_courses = cart.courses()
        items.extend([item.token for item in cart_courses])

        if not cart_courses:
            messages.error(request, "Your cart is empty.")
            return redirect("cart:cart_detail")
    host = request.get_host()
    courses = Course.objects.filter(token__in=items)
    enrolled_courses = Enrollment.objects.filter(
        user=request.user, course__token__in=items
    )
    if enrolled_courses:
        enrolled_tokens = [enrollment.course.token for enrollment in enrolled_courses]
        enrolled_titles = [enrollment.course.title for enrollment in enrolled_courses]

        # override on courses
        courses = courses.exclude(token__in=enrolled_tokens)
        # update the items with new tokens not in the  enrolled tokens list
        items = [token for token in items if token not in enrolled_tokens]
        for token in enrolled_tokens:
            cart.remove_item(token)

        messages.info(
            request,
            f"We removed: {', '.join(enrolled_titles)}. You are already enrolled.",
        )

    total = sum([item.discount if item.discount else item.price for item in courses])

    if total == 0:
        messages.info(request, "No items to purchase.")
        return redirect("course:course-list")

    paypal_dict = {
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "amount": f"{total:.2f}",
        "item_name": ", ".join([course.title for course in courses]),
        "invoice": str(uuid.uuid4()),
        "currency_code": "USD",
        "no_shipping": "2",
        # "notify_url": f"https://{host}{reverse('paypal-ipn')}",
        "return_url": f"https://{host}{reverse('payment:payment-success')}",
        "cancel_url": f"https://{host}{reverse('payment:payment-failed')}",
        "cmd": "_xclick",
        "charset": "utf-8",
    }

    paypal_form = PayPalPaymentsForm(initial=paypal_dict)

    request.session["pending_purchase"] = {
        "courses_tokens": items,
        "total": str(total),
    }

    context = {
        "paypal_form": paypal_form,
        "amount": str(total),
        "items": courses,
    }
    return render(request, "payment/checkout.html", context)


def payment_success(request):
    enrollments_created = []
    cart = Cart(request)

    with transaction.atomic():
        try:
            pending_purchase = request.session.get("pending_purchase")
            if not pending_purchase:
                messages.error(request, "No pending purchase found.")
                return redirect("course:courses-list")

            courses_tokens = pending_purchase.get("courses_tokens")
            if not courses_tokens:
                messages.error(request, "No courses found in pending purchase.")
                return redirect("course:courses-list")

            courses = Course.objects.filter(token__in=courses_tokens)
            for course in courses:
                enrollment, created = Enrollment.objects.get_or_create(
                    user=request.user, course=course
                )
                if created:
                    enrollments_created.append(enrollment.course.title)
            # clear the cart
            cart_courses = cart.courses()
            if cart_courses:
                for course in courses:
                    if course in cart_courses:
                        cart.remove_item(course.token)

            # delete the session after success payment
            if "pending_purchase" in request.session:
                del request.session["pending_purchase"]
            messages.success(
                request, f"Successfully enrolled in: {', '.join(enrollments_created)}"
            )
        except Exception as ex:
            messages.error(request, f"Failed to create enrollments: {ex}")
            return redirect("/")
    context = {"courses": courses, "enrollments": enrollments_created}
    return render(request, "payment/success_payment.html", context)


def payment_failed(request):
    return render(request, "payment/fails_payment.html")
