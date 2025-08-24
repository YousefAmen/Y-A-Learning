import json
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View

# Import your models
from course.models import Course, Enrollment
from cart.cart import Cart

logger = logging.getLogger(__name__)


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
    total = sum([item.price for item in courses])
    if total == 0:
        messages.info(request, "No items to purchase.")
        return redirect("courses:course-list")

    context = {
        "amount": str(total),
        "items": courses,
        "PAYPAL_CLIENT_ID": settings.PAYPAL_CLIENT_ID,
    }
    return render(request, "payment/checkout.html", context)

    # paypal_dict = {
    #     "business": settings.PAYPAL_RECEIVER_EMAIL,
    #     "amount": str(total),
    #     "item_name": ", ".join([course.title for course in courses]),
    #     "invoice": str(uuid.uuid4()),
    #     "currency_code": "USD",
    #     "no_shipping": "2",
    #     "notify_url": f"https://{host}{reverse('paypal-ipn')}",
    #     "return_url": f"https://{host}{reverse('payment:payment-success')}",
    #     "cancel_url": f"https://{host}{reverse('payment:payment-failed')}",
    # }
    # paypal_form = PayPalPaymentsForm(initial=paypal_dict)
    # for item in items:
    #     enrollment = Enrollment.objects.create(user=request.user, course=item)
    # "paypal_form": paypal_form,


@login_required
@require_POST
def payment_success(request):
    """Handle successful PayPal payment"""
    try:
        # Parse JSON data from PayPal
        data = json.loads(request.body)
        order_id = data.get("orderID")
        payer_id = data.get("payerID")
        payment_details = data.get("paymentDetails")
        amount = data.get("amount")

        logger.info(
            f"Payment success for user {request.user.id}: OrderID={order_id}, Amount=${amount}"
        )

        if not all([order_id, payer_id, payment_details]):
            logger.error("Missing payment data in success callback")
            return JsonResponse(
                {"success": False, "message": "Missing payment information"}, status=400
            )

        # Get cart and process enrollment
        cart = Cart(request)
        cart_courses = cart.courses()

        # If no cart courses, this might be a direct purchase
        if not cart_courses:
            # Try to get course from session or other means
            # You might need to store the purchase intent in session
            logger.warning("No cart courses found during payment success")

        total_enrolled = 0
        enrolled_course_titles = []

        for course in cart_courses:
            # Check if user is not already enrolled
            if not Enrollment.objects.filter(user=request.user, course=course).exists():
                # Create enrollment
                Enrollment.objects.create(
                    user=request.user,
                    course=course,
                )
                enrolled_course_titles.append(course.title)
                total_enrolled += 1
                logger.info(f"Enrolled user {request.user.id} in course {course.id}")

        # Clear cart after successful enrollment
        cart.clear()

        # Add success message
        if total_enrolled > 0:
            messages.success(
                request,
                f"Payment successful! You've been enrolled in {total_enrolled} course(s): {', '.join(enrolled_course_titles)}",
            )

        # Store payment details in session for receipt
        request.session["last_payment"] = {
            "order_id": order_id,
            "amount": amount,
            "courses": enrolled_course_titles,
            "payer_name": payment_details.get("payer", {})
            .get("name", {})
            .get("given_name", "Student"),
        }

        return JsonResponse(
            {
                "success": True,
                "message": f"Successfully enrolled in {total_enrolled} course(s)",
                "redirect_url": reverse("payment:payment-complete"),
            }
        )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in payment success callback")
        return JsonResponse(
            {"success": False, "message": "Invalid payment data format"}, status=400
        )

    except Exception as e:
        logger.error(f"Payment success processing error: {str(e)}")
        return JsonResponse(
            {"success": False, "message": "Payment processing failed"}, status=500
        )


def payment_failed(request):
    return render(request, "payment/fails_payment.html")
