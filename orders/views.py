from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
import datetime

from .models import OrderProduct, Order, Payment
from store.models import Product
from carts.models import CartItem
from .forms import OrderForm

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests


def payments(request):
  body = json.loads(request.body)
  order = Order.objects.get(user=request.user, order_number=body['orderID'], is_ordered=False)
  # print(body)
  payment = Payment()
  payment.user = request.user
  payment.payment_id = body['transID']
  payment.payment_method = body['payment_method']
  payment.status = body['status']
  payment.amount_paid = body['amount']

  payment.save()
  order.payment = payment
  order.is_ordered = True
  order.save()

  # Move the cart_items to product table
  cart_items = CartItem.objects.filter(user=request.user)
  list_of_products = []

  for item in cart_items:
    orderproduct = OrderProduct()
    orderproduct.order_id = order.id
    orderproduct.user_id = request.user.id
    orderproduct.payment = payment
    orderproduct.product_id = item.product_id
    orderproduct.quantity = item.quantity
    orderproduct.product_price = item.product.price
    orderproduct.ordered = True
    list_of_products.append(item.product.product_name)
    orderproduct.save()

    cart_item = CartItem.objects.get(id=item.id)
    product_variation = cart_item.variations.all()
    orderproduct = OrderProduct.objects.get(id=orderproduct.id)
    orderproduct.variations.set(product_variation)
    orderproduct.save()

    # Reduce the quanitity of sold product from store
    product = Product.objects.get(id=item.product.id)
    product.stock -= orderproduct.quantity
    product.save()

  # Clear the cart after order is places
  CartItem.objects.filter(user=request.user).delete()

  # Send order completion mail to user
  current_site = get_current_site(request)
  mail_subject = 'Thank for ordering from our site!'
  message = render_to_string('orders/order_received_mail.html', {
    'user' : request.user,
    'order': order,
    'products': list_of_products,
  })
  to_email = request.user.email
  send_email = EmailMessage(mail_subject, message, to=[to_email])
  send_email.send()

  data = {
    'order_number' : order.order_number,
    'transID' : payment.payment_id
  }

  return JsonResponse(data)

def place_order(request, total=0, quanitity=0):
  current_user = request.user

  cart_items = CartItem.objects.filter(user=current_user)
  cart_count = cart_items.count()
  if cart_count <= 0:
    return redirect('store')

  grand_total = 0
  tax = 0

  for item in cart_items:
    total += (item.product.price) * (item.quantity)
    quanitity += item.quantity

  tax = (2*total)/100
  grand_total = total + tax


  if request.method == 'POST': 

    form = OrderForm(request.POST)
    if form.is_valid():
      data = Order()
      data.user = current_user
      data.first_name = form.cleaned_data['first_name']
      data.last_name = form.cleaned_data['last_name']
      data.email = form.cleaned_data['email']
      data.phone = form.cleaned_data['phone']
      data.address_line_1 = form.cleaned_data['address_line_1']
      data.address_line_2 = form.cleaned_data['address_line_2']
      data.state = form.cleaned_data['state']
      data.city = form.cleaned_data['city']
      data.country = form.cleaned_data['country']
      data.pin_code = form.cleaned_data['pin_code']
      data.order_note = form.cleaned_data['order_note']
      data.order_total = grand_total
      data.tax = tax
      data.ip = request.META.get('REMOTE_ADDR')
      data.save()

      # Generate order number
      yr = int(datetime.date.today().strftime('%y'))
      dt = int(datetime.date.today().strftime('%d'))
      mt = int(datetime.date.today().strftime('%m'))
      d = datetime.date(yr,mt,dt)
      current_date = d.strftime("%Y%m%d")
      order_number = current_date + str(data.id)

      data.order_number = order_number
      data.save()

      order = Order.objects.get(user=current_user, order_number=order_number, is_ordered=False)
      context = {
        'order' : order,
        'cart_items': cart_items,
        'total': total,
        'tax':tax,
        'grand_total':grand_total,
      }
      return render(request, 'orders/payments.html', context)

  else:
    return redirect('checkout')

def order_complete(request):
  order_number = request.GET.get('order_number')
  transID = request.GET.get('payment_id')
  grand_total = 0
  try:
    order = Order.objects.get(order_number=order_number, is_ordered=True)
    ordered_products = OrderProduct.objects.filter(order_id=order.id)
    
    payment = Payment.objects.get(payment_id=transID)

    subtotal = 0
    for item in ordered_products:
      subtotal += item.product_price * item.quantity

    context = {
      'order' : order,
      'ordered_products' : ordered_products,
      'order_number' : order_number,
      'transID' : payment.payment_id,
      'payment' : payment,
      'subtotal' : subtotal,
    }

    return render(request, 'orders/order_complete.html', context)
  
  except (Order.DoesNotExist, Payment.DoesNotExist):
    return redirect('home')
    
  return render(request, 'orders/order_complete.html')
  