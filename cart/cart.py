
from course.models import Course


class Cart:
  def __init__(self,request):
    self.session = request.session
    cart = self.session.get('cart')
    if not cart:
      cart = self.session['cart'] = {}
    self.cart = cart

  def save(self):
    self.session.modified =True
  def add_item(self,course):
    if course.token not in self.cart:
        self.cart[course.token] = {
          "name":course.title,
          "price":str(course.price)
      }    
        self.save()
    else:
      return self.cart[course.token]
    
  def remove_item(self,course):
    if course.token in self.cart:
        del self.cart[course.token]
        self.save()

  def total_amount(self):
    return sum(float(item['price']) for item in self.cart.values())
  def __len__(self):
    return len(self.cart)
  def courses(self):
    keyes=self.cart.keys()
    courses = Course.objects.filter(token__in = keyes)
    return courses