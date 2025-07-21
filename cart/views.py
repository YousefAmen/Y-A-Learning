from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from course.models import Course

from .cart import Cart


def add_to_cart(request):
  if request.method == "POST" and request.POST.get("action") == "post":
    token = request.POST.get('token')
    course = get_object_or_404(Course, token=token)
    cart = Cart(request)
    cart.add_item(course)
    return JsonResponse({
    'success': True,
    'total_amount': cart.total_amount(),
    'item_count': len(cart),
  })
  

def remove_from_cart(request):
  if request.method == "POST" and request.POST.get("action") == "post":
    token = request.POST.get('token')
    course = get_object_or_404(Course, token=token)
    cart = Cart(request)
    cart.remove_item(course)
    return JsonResponse({
    'success': True,
    'total_amount': cart.total_amount(),
    'item_count': len(cart),
  })
  

def cart_detail(request):
  cart  = Cart(request)
  courses = cart.courses()
  return render(request,'cart/cart_detail.html',{"cart":cart,"courses":courses})
  