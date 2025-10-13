from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .admin_forms import CouponcartForm, AddressForm
import razorpay
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User

# Create your views here.

from django.core.paginator import Paginator

def home(request):
    products = Product.objects.all()

    # Check if search query exists
    search_query = request.GET.get('search')
    if search_query:
        filter_products = products.filter(brand__icontains=search_query)
        if filter_products.exists():
          paginator = Paginator(products, 12)  
          page_number = request.GET.get("page")
          page_obj = paginator.get_page(page_number)

          return render(request, "public/allproduct.html", {"page_obj": page_obj,"search_query": search_query})
    

        paginator = Paginator(products, 12)  
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request, "public/main.html", {"page_obj": page_obj})

    paginator = Paginator(products, 12)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    has_order = False
    try:
      if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, isordered = True).exists()
        if order:
          has_order = True
    except:
      has_order = False

    return render(request, "public/main.html", {"page_obj": page_obj, "has_order":has_order})

def registeruser(request):

  if request.method == "POST":
    first_name = request.POST.get("first name")
    last_name = request.POST.get("last name")
    username = request.POST.get("username")
    email = request.POST.get("email")
    pass1 = request.POST.get("password1")
    pass2 = request.POST.get("password2")
    if pass1==pass2:
      user = User()
      user.first_name = first_name
      user.last_name = last_name
      user.username = username
      user.email = email
      user.set_password(pass1)
      user.save()

      login(request,user)
      return redirect("homepage")
    else:
      messages.error(request, "password did not match")

  return render(request,"registration/register.html")

def viewproduct(request,id):
  products = Product.objects.get(id=id)
  categories = Category.objects.all()
  items = Product.objects.exclude(pk=id)
  return render(request, 'public/viewproduct.html',{'products':products, "categories":categories, "items":items})

def products(request,id=None):
  categories = Category.objects.all()

  context ={}
  if id is not None:
    filter_products = Product.objects.filter(category = id)
    context["filter_category"] = get_object_or_404(Category,id=id)
    context["numbers"] = filter_products.count()
    paging = Paginator(filter_products,16)
  else:
    products = Product.objects.all()
    context["no_of_products"] = products.count()
    paging = Paginator(products,16)
  
  page_number = request.GET.get("page")
  page_obj = paging.get_page(page_number)
  
  context["page_obj"] = page_obj
  context["categories"] = categories

  return render(request,"public/allproduct.html",context)


@login_required
def buynow(request,id):
  product = get_object_or_404(Product,id = id)  

  addresses = Address.objects.filter(user=request.user)
  if addresses.exists():
    last_address = addresses.last()

  order = Order.objects.filter(user=request.user,isordered=False,from_buynow=True)

  if order.exists():
    order = order[0]
    OrderItem.objects.filter(user=request.user,isordered=False,order_id=order).delete()
    order.coupon_id = None
    order.address = last_address if addresses else None
    order.save()
  else:
    order = Order()
    order.user = request.user
    order.from_buynow = True
    order.address = last_address if addresses else None
    order.save()

  orderitem = OrderItem()
  orderitem.user = request.user
  orderitem.isordered = False
  orderitem.product_id = product
  orderitem.order_id = order
  orderitem.save()

  return redirect(checkoutaddress,id=order.id)

@login_required
def checkoutaddress(request,id):
  order = get_object_or_404(Order,user=request.user,isordered=False,id=id)
  orderitems = OrderItem.objects.filter(user=request.user,order_id=id,isordered=False)
  product_no = int(orderitems.count())
  addresses = Address.objects.filter(user=request.user)

  form = AddressForm(request.POST or None)
  couponform = CouponcartForm(request.POST or None)

  show_form = False

  if request.GET.get("add_new_address") == "true":
    show_form = True

  if  request.method == "POST":
    if form.is_valid():
      address = form.save(commit=False)
      address.user = request.user
      address.save()

      order.address = address
      order.save()
      messages.success(request,"Address has been saved successfully")
      show_form = False
      return redirect('address',id = order.id)
    else:
      show_form = True

  selected_address_id = request.POST.get("address")
  if selected_address_id:
    order.address = Address.objects.filter(id=selected_address_id,user=request.user)

  other_addresses = None
  if order.address:
    selected_address = order.address
    other_addresses = addresses.exclude(id=selected_address.id)
  
  
  if not addresses.exists():
    show_form = True

  context = {
    "product_no":product_no,
    "form":form,
    "order":order,
    "orderitems":orderitems,
    "other_addresses":other_addresses,
    "selected_address":selected_address,
    "couponform":couponform,
    "show_form":show_form,
    }
    
  return render(request, 'public/address.html',context)

def addAddressInfo(request):
  if request.method == 'POST':
    order = Order.objects.filter(user=request.user, isordered=False).last()
    if order:
      address_id = request.POST.get('address')
      address = Address.objects.get(pk=address_id)
      if address:
        order.address = address
        order.save()
        messages.success(request,"Address has been saved successfully")
        return redirect(checkoutaddress, id=order.id)
    else:
      return redirect(cart)  

@login_required
def addtocart(request,product_id):
  product = get_object_or_404(Product,id = product_id)
  
  addresses = Address.objects.filter(user=request.user)
  if addresses.exists():
    last_address = addresses.last()

  orders = Order.objects.filter(user=request.user, isordered = False,from_buynow=False)

  if orders.exists():
    order = orders[0]
    existorderitem = OrderItem.objects.filter(user=request.user,isordered=False,product_id=product,order_id=order).exists()
    order.address = last_address if addresses else None


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
    o.from_buynow = False
    o.address = last_address if addresses else None
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
  addresses = Address.objects.filter(user=request.user)
  if addresses.exists():
    last_address = addresses.last()
  order = Order.objects.filter(user=request.user,isordered = False,from_buynow=False).first()
  if order:
    orderitems = OrderItem.objects.filter(user=request.user,isordered = False,order_id = order)
  else:
    order = Order()
    order.user = request.user
    order.from_buynow = False
    order.address = last_address if addresses else None
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


@login_required()
def buynowaddCoupon(request,id):
  if request.method == "POST":
    code = request.POST.get("code")
    coupon  = Coupon.objects.filter(code=code).first()
    if coupon:
        order = Order.objects.filter(user=request.user, isordered=False,id=id).first()
        if order.getpayableamount() > coupon.amount:
          order.coupon_id = coupon
          order.save()
        else:
          messages.add_message(request,messages.ERROR,  message="this Coupon is not applicable in this Order Amount")
    else:
      messages.add_message(request, messages.ERROR, message="This coupon is invalid or Expired")
  return redirect(checkoutaddress,id=order.id)

@login_required()
def removecouponfrombuynow(request, coupon_id):
  coupon  = Coupon.objects.get(id=coupon_id)

  order = Order.objects.filter(user=request.user, isordered=False).last()
  if coupon:
    order.coupon_id = None
    order.save()
    return redirect(checkoutaddress,id=order.id) 

@login_required()
def addCoupon(request):
  if request.method == "POST":
    code = request.POST.get("code")
    coupon  = Coupon.objects.filter(code=code).first()
    if coupon:
        order = Order.objects.filter(user=request.user, isordered=False).first()
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
  order = Order.objects.filter(user=request.user, isordered=False,from_buynow=False).last()
  if coupon:
    order.coupon_id = None
    order.save()
    return redirect(cart) 
  
@login_required
def payment(request):
  order = Order.objects.filter(user=request.user, isordered=False).first()
  if not order:
      messages.error(request, "No active order found. Please add items to your cart first.")
      return redirect('cart')
  
  if order.address:
    if request.method == "POST":
      order.isordered = True
      orderitems = OrderItem.objects.filter(order_id=order.id)
      total = 0
      for item in orderitems:
        item.isordered =True
        item.product_dis_price_at_order = item.product_id.dis_price
        item.product_price_at_order = item.product_id.price
        item.save()
        total += item.product_dis_price_at_order * item.qty

        if order.coupon_id:
          total -= order.coupon_id.amount
      
      order.price_at_order = total
      order.save()
      return redirect("ordercomplete")
    
    client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
    payment = client.order.create({'amount': order.getpayableamount()*100 , 'currency': 'INR', 'payment_capture': 1})
    order.razor_pay_order_id = payment['id']
    order.save()
    return render(request, 'public/make-payment.html', {'payment':payment})
  else:
    return redirect('address', id=order.id)
  

    
def ordercomplete(request):
  order_id = request.GET.get('razorpay_order_id')
  
  order = Order.objects.get(razor_pay_order_id = order_id)
  order.isordered = True
  order.save()
  order_items = OrderItem.objects.filter(order_id = order)
  total = 0
  for item in order_items:
    item.isordered = True
    item.product_dis_price_at_order = item.product_id.dis_price
    item.product_price_at_order = item.product_id.price
    item.save()
    total += item.product_dis_price_at_order*item.qty
    if order.coupon_id:
          total -= order.coupon_id.amount
      
  order.price_at_order = total
  order.save()
  return render(request, 'public/success_page.html')

@login_required
def my_order(request):

    orders = Order.objects.filter(user=request.user, isordered=True)
  
    data = {
      "orders":orders,
    }
    return render(request, "public/my_order.html", data)
