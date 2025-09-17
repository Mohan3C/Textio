from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .admin_forms import CouponcartForm, AddressForm

# Create your views here.

def home(request):
  products = Product.objects.all()
  return render(request,"public/main.html",{"products":products})

def viewproduct(request,id):
  products = Product.objects.get(id=id)
  return render(request, 'public/viewproduct.html',{'products':products})

def products(request):
  categories = Category.objects.all()
  products = Product.objects.all()
  return render(request,"public/allproduct.html",{"products":products, "categories":categories})



def registeruser(request):

  if request.method == "POST":
    form = UserCreationForm(request.POST)

    if form.is_valid():
      user=form.save()
      login(request,user)
      return redirect("homepage")  
  else:
    form = UserCreationForm()

  return render(request,"registration/register.html", {"form":form})


@login_required
def filter_product(request,id):
  categories = Category.objects.all()
  products = Product.objects.filter(category_id = id)
  paging = Paginator(products,8)
  page_number = request.GET.get('page')
  page_obj = paging.get_page(page_number)
  
  return render(request,"main.html",{"categories":categories,"page_obj":page_obj})

def buynow(request,id):
  product = get_object_or_404(Product,id = id)  
   
  
  


  o = Order()
  o.user = request.user
  o.save()
  oi = OrderItem()
  oi.user = request.user
  oi.isordered = False
  oi.product_id = product
  oi.order_id = o

  return redirect(checkoutaddress,id)

@login_required
def checkoutaddress(request,id):
  order = Order.objects.filter(user=request.user,isordered = False).first()
  orderitems = OrderItem.objects.filter(user=request.user,order_id = order)
  product = Product.objects.filter(id=id)
 
  

  form = AddressForm(request.POST or None)
 

  if  request.method == "POST":
    if form.is_valid():
      address = form.save(commit=False)
      address.user = request.user
      address.save()

      order.address_id = address
      order.save()
      return redirect('address',id = order.id)
  return render(request, 'public/address.html',{"product":product,"form":form,"order":order,"orderitems":orderitems})



@login_required
def addtocart(request,product_id):
  product = get_object_or_404(Product,id = product_id)
  
  orders = Order.objects.filter(user=request.user, isordered = False)

  if orders.exists():
    order = orders[0]
    existorderitem = OrderItem.objects.filter(user=request.user,isordered=False,product_id=product,order_id=order).exists()

    if existorderitem:
      existoi = OrderItem.objects.get(user=request.user,isordered=False,product_id=product,order_id=order)
      existoi.qty += 1
      existoi.save()
    else:
      oi = OrderItem()
      oi.user = request.user
      oi.isordered = False
      oi.product_id = product
      oi.order_id = order
      
      oi.save()
  else:
    o = Order()
    o.user = request.user
    o.save()

    oi = OrderItem()
    oi.user = request.user
    oi.isordered = False
    oi.product_id = product
    oi.order_id = o
    
    oi.save()

  return redirect("cart")

@login_required()
def cart(request):
  order = Order.objects.filter(user=request.user,isordered = False).first()
  if order:
    orderitems = OrderItem.objects.filter(user=request.user,isordered = False,order_id = order)
  else:
    order = Order()
    order.user = request.user
    order.save()

  orderitems = OrderItem.objects.filter(order_id=order,user=request.user)
  form = CouponcartForm(request.POST or None)
  return render(request,"public/cart.html",{"order":order,"orderitems":orderitems,"form":form})



@login_required
def removefromcart(request,product_id):
  product = get_object_or_404(Product,id = product_id)
  
  orders = Order.objects.filter(user=request.user, isordered = False)

  if orders.exists():
    order = orders[0]
    existorderitem = OrderItem.objects.filter(user=request.user,isordered=False,product_id=product,order_id=order).exists()

    if existorderitem:
      existoi = OrderItem.objects.get(user=request.user,isordered=False,product_id=product,order_id=order)

      if existoi.qty >1:
        existoi.qty -= 1
        existoi.save()
      else:
        existoi.delete()

  return redirect("cart")


@login_required
def deletefromcart(request,product_id):
  product = get_object_or_404(Product,id = product_id)
  
  orders = Order.objects.filter(user=request.user, isordered = False)

  if orders.exists():
    order = orders[0]
    existorderitem = OrderItem.objects.filter(user=request.user,isordered=False,product_id=product,order_id=order).exists()

    if existorderitem:
      existoi = OrderItem.objects.get(user=request.user,isordered=False,product_id=product,order_id=order)

      existoi.delete()

  return redirect("cart")


@login_required
def ordercomplete(request):
  
  orders = Order.objects.filter(user=request.user, isordered = False).first()

  if orders:
    orders.isordered = True
    orders.save()
   
    order_items = OrderItem.objects.filter(user= request.user,order_id=orders,isordered=False)
    for item in order_items:
      item.isordered = True
      item.save()

  return render(request,"ordercomplete.html")


@login_required()
def addCoupon(request):
  if request.method == "POST":
    code = request.POST.get("code")
    coupon  = Coupon.objects.filter(code=code).first()
    if coupon:
        order = Order.objects.get(user=request.user, isordered=False)
        if order.getpayableamount() > coupon.amount:
          order.coupon_id = coupon
          order.save()
        else:
          messages.add_message(request,messages.ERROR,  message="this Coupon is not applicable in this Order Amount")
    else:
      messages.add_message(request, messages.ERROR, message="This coupon is invalid or Expired")
  return redirect(cart)             

        
@login_required()
def RemoveCoupon(request, coupon_id):
  coupon  = Coupon.objects.get(id=coupon_id)
  if coupon:
    order = Order.objects.get(user=request.user, isordered=False)
    order.coupon_id = None
    order.save()
    return redirect(cart) 
  
@login_required
def payment(request):
  order = Order.objects.get(user=request.user, isordered=False)
  if not order:
      messages.error(request, "No active order found. Please add items to your cart first.")
      return redirect('cart')
  
  if order.address:
    if request.method == "POST":
      order.isordered = True
      orderitems = OrderItem.objects.filter(order_id=order.id)
      for item in orderitems:
        item.isordered =True
        item.save()
      order.save()
    return render(request, 'public/make-payment.html')
  else:
    return redirect('address', id=order.id)
    
  