from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import *
from .admin_forms import CouponcartForm, AddressForm
import razorpay
from django.conf import settings
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import os
import random

# Create your views here.

from django.core.paginator import Paginator


#  i add this for debugging
import logging
logger = logging.getLogger(__name__)
    


def registeruser(request):

  if request.method == "POST":
    username = request.POST.get("username")
    email = request.POST.get("email")
    pass1 = request.POST.get("password1")
    pass2 = request.POST.get("password2")
    if pass1==pass2:
      user = User()
      user.username = username
      user.email = email
      user.set_password(pass1)
      user.save()

      login(request,user)
      return redirect("homepage")
    else:
      messages.error(request, "password did not match")

  return render(request,"registration/register.html")


def assign_item_to_order(request,guest_user,user):
  temp_orders = Order.objects.filter(temp_user=guest_user,isordered=False,from_buynow=False)

  if not temp_orders.exists():
    return 

  user_order = Order.objects.filter(user=user,isordered=False,from_buynow=False).first()

  for temp_order in temp_orders:

    orderitems = OrderItem.objects.filter(isordered=False,order_id=temp_order)
    if orderitems.exists():

      for item in orderitems:
        if user_order:
          existitem = OrderItem.objects.filter(isordered=False,variant_product=item.variant_product,order=user_order).first()

          if existitem:
            existitem.qty += 1
            existitem.save()
          else:
            orderitem = OrderItem()
            orderitem.order = user_order
            orderitem.variant_product = item.variant_product
            orderitem.isordered =False
            orderitem.save()
        else:
          user_order = Order()
          user_order.user = user
          user_order.isordered=False
          user_order.from_buynow=False
          user_order.save()

          orderitem = OrderItem()
          orderitem.order = user_order
          orderitem.variant_product = item.variant_product
          orderitem.isordered =False
          orderitem.save()

    temp_order.delete()

  request.session.pop('guest_user',None)


def user_login(request):
 
  guest_user = request.session.get('guest_user')

  if request.method == 'POST':
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request,username=username,password=password)
    if user is not None:
      if guest_user:
        assign_item_to_order(request,guest_user,user)

      login(request,user)

      next_url = request.POST.get('next') or 'homepage'
      return redirect(next_url)
    else:
      return redirect("login_user")
  return render(request,"registration/login.html")

def home(request):
    
    # for random product in home page 
    products = list(Product.objects.prefetch_related('variants'))
    random.shuffle(products)
  
    for product in products:
      product.first_variant = product.variants.first()



    # Check if search query exists
    # search_query = request.GET.get('search')
    # if search_query:
    #     filter_products = products.filter(Q(brand__icontains=search_query))
    #     filter_category = category.filter(Q(name__icontains=search_query))
    #     if filter_products.exists():
    #       paginator = Paginator(products, 12)  
    #       page_number = request.GET.get("page")
    #       page_obj = paginator.get_page(page_number)

    #       return render(request, "public/allproduct.html", {"page_obj": page_obj,"search_query": search_query})
    

    #     paginator = Paginator(products, 12)  
    #     page_number = request.GET.get("page")
    #     page_obj = paginator.get_page(page_number)

    #     return render(request, "public/main.html", {"page_obj": page_obj})

    paginator = Paginator(products, 12)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "public/main.html", {"page_obj": page_obj})

def temp_User(request):

  guest_user = request.session.get("guest_user")

  if not guest_user:
    guest_user = f"Guest_{random.randint(10000,99999)}"
    request.session['guest_user']= guest_user

  return guest_user

def profile(request):
  return render(request,"registration/profile.html")


def viewproduct(request,id):
  product = Product.objects.prefetch_related('variants').get(id=id)

  variants = product.variants.all()
  display_variant = variants.first()

  selected_size = request.GET.get('size') or None
  selected_color = request.GET.get("color") or None

  color_variants = []
  colors = set()

  for v in variants:
    if v.color not in colors:
      color_variants.append(v)
      colors.add(v.color)

  size_variants = []
  sizes = set()

  for v in variants:
    if v.size not in sizes:
      size_variants.append(v)
      sizes.add(v.size)
  
  if selected_color and selected_size:
    display_variant = variants.filter(color=selected_color,size=selected_size).first()
    display_variant = variants.filter(color = selected_color,size=selected_size).first()

    available_sizes = list(set(variants.filter(color=selected_color).values_list('size__id', flat=True)))
    available_colors = list(set(variants.filter(size=selected_size).values_list('color', flat=True)))
  elif selected_color:
    display_variant = variants.filter(color=selected_color).first()

    available_sizes = list(set(variants.filter(color=selected_color).values_list('size__id', flat=True)))
    available_colors = list(set(variants.values_list('color', flat=True)))
  elif selected_size:
    display_variant = variants.filter(size=selected_size).first()

    available_colors = list(set(variants.filter(size=selected_size).values_list('color', flat=True)))
    available_sizes = list(set(variants.values_list('size__id', flat=True)))
  else:
    available_sizes = list(set(variants.values_list('size__id', flat=True)))
    available_colors = list(set(variants.values_list('color', flat=True)))

  items = Product.objects.exclude(pk=id).filter(category = product.category)
  for item in items:
    item.first_variant = item.variants.first()

  context = {
    "product":product,
    'display_variant':display_variant,
    'color_variants':color_variants,
    'size_variants':size_variants,
    'selected_color':selected_color,
    'selected_size':selected_size,
    'available_colors':available_colors,
    'available_sizes':available_sizes,
    "items":items,
  }
  
  return render(request, 'public/viewproduct.html',context)

def products(request,id=None):
  categories = Category.objects.all()

  context ={}
  if id is not None:
    filter_products = list(Product.objects.prefetch_related('variants').filter(category = id))
    random.shuffle(filter_products)

    for product in filter_products:
      product.display_variant = product.variants.first()

    context["filter_category"] = get_object_or_404(Category,id=id)
    context["numbers"] = len(filter_products)
    paging = Paginator(filter_products,16)
  else:
    products = list(Product.objects.all())
    random.shuffle(products)

    for product in products:
      product.display_variant = product.variants.first()

    context["no_of_products"] = len(products)
    paging = Paginator(products,16)
  
  page_number = request.GET.get("page")
  page_obj = paging.get_page(page_number)
  
  context["page_obj"] = page_obj
  context["categories"] = categories

  return render(request,"public/allproduct.html",context)


def buynow(request,id):
  if request.user.is_authenticated:
    product = get_object_or_404(Variant,id = id)  

    addresses = Address.objects.filter(user=request.user)
    if addresses.exists():
      last_address = addresses.last()

    order = Order.objects.filter(user=request.user,isordered=False,from_buynow=True)

    if order.exists():
      order = order[0]
      OrderItem.objects.filter(isordered=False,order=order).delete()
      order.coupon = None
      order.address = last_address if addresses else None
      order.save()
    else:
      order = Order()
      order.user = request.user
      order.from_buynow = True
      order.address = last_address if addresses else None
      order.save()

    orderitem = OrderItem()
    orderitem.isordered = False
    orderitem.variant_product = product
    orderitem.order = order
    orderitem.save()

    return redirect(checkoutaddress,id=order.id)
  else:
    return redirect("addtocart",id)

@login_required
def checkoutaddress(request,id):
  order = get_object_or_404(Order,user=request.user,isordered=False,id=id)
  orderitems = OrderItem.objects.filter(order=order,isordered=False)
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

  selected_address = None
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


def addtocart(request,variant_id):
  if request.user.is_authenticated:
    product = get_object_or_404(Variant, id = variant_id)
  
    addresses = Address.objects.filter(user=request.user)
    if addresses.exists():
      last_address = addresses.last()

    orders = Order.objects.filter(user=request.user, isordered = False,from_buynow=False)

    if orders.exists():
      order = orders[0]
      existorderitem = OrderItem.objects.filter(isordered=False,variant_product=product,order=order). exists()
      order.address = last_address if addresses else None


      if existorderitem:
        existoi = OrderItem.objects.get(isordered=False,variant_product=product,order=order)
        existoi.qty += 1
        existoi.save()
      else:
        oi = OrderItem()
        oi.isordered = False
        oi.variant_product = product
        oi.order = order
      
        oi.save()
    else:
      o = Order()
      o.user = request.user
      o.from_buynow = False
      o.address = last_address if addresses else None
      o.save()

      oi = OrderItem()
      oi.isordered = False
      oi.variant_product = product
      oi.order = o
    
      oi.save()

    return redirect("cart")
  else:
    product = get_object_or_404(Variant,id = variant_id)
    user = temp_User(request)

    orders = Order.objects.filter(temp_user = user, isordered = False,from_buynow=False)

    if orders.exists():
      order = orders[0]
      existorderitemi = OrderItem.objects.filter(isordered=False,variant_product=product,order=order). exists()

      if existorderitemi:
        existoi = OrderItem.objects.get(isordered=False,variant_product=product,order=order)
        existoi.qty += 1
        existoi.save()
      else:
        oi = OrderItem()
        oi.isordered = False
        oi.variant_product = product
        oi.order = order
        oi.save()
    else:
      o = Order()
      o.temp_user = user
      o.save()

      oi = OrderItem()
      oi.isordered = False
      oi.variant_product = product
      oi.order = o
    
      oi.save()

    return redirect("cart")


def cart(request):
  form = CouponcartForm(request.POST or None)
  if request.user.is_authenticated:
    addresses = Address.objects.filter(user=request.user)
    if addresses.exists():
      last_address = addresses.last()
    order = Order.objects.filter(user=request.user,isordered = False,from_buynow=False).first()
   
    orderitems = None
    if order:
      orderitems = OrderItem.objects.filter(order=order,isordered = False)
    

    return render(request,"public/cart.html",{"order":order,"orderitems":orderitems,"form":form})
  else:
    user = temp_User(request)

    
    order = Order.objects.filter(temp_user=user).first()
    if not order:
      order = Order()
      order.temp_user = user
      order.save()

      
    orderitems = OrderItem.objects.filter(isordered=False,order=order)
      
    return render(request,"public/cart.html",{"order":order,"orderitems":orderitems,"form":form})


def removefromcart(request,variant_id):
  product = get_object_or_404(Variant,id = variant_id)
  
  if request.user.is_authenticated:
    orders = Order.objects.filter(user=request.user, isordered = False)
  else:
    user = temp_User(request)

    orders = Order.objects.filter(temp_user=user)


  if orders.exists():
    order = orders[0]
    existorderitem = OrderItem.objects.filter(isordered=False,variant_product=product,order=order).exists()

    if existorderitem:
      existoi = OrderItem.objects.get(isordered=False,variant_product=product,order=order)

      if existoi.qty >1:
        existoi.qty -= 1
        existoi.save()
      else:
        existoi.delete()

  return redirect("cart")



def deletefromcart(request,variant_id):
  product = get_object_or_404(Variant,id = variant_id)
  
  if request.user.is_authenticated:
    orders = Order.objects.filter(user=request.user, isordered = False)
  else:
    user = temp_User(request)

    orders = Order.objects.filter(temp_user=user)

  if orders.exists():
    order = orders[0]
    existorderitem = OrderItem.objects.filter(isordered=False,variant_product=product,order=order).exists()

    if existorderitem:
      existoi = OrderItem.objects.get(isordered=False,variant_product=product,order=order)

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
          order.coupon = coupon
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
    order.coupon = None
    order.save()
    return redirect(checkoutaddress,id=order.id) 


def addCoupon(request):
  if request.method == "POST":
    code = request.POST.get("code")
    coupon  = Coupon.objects.filter(code=code).first()
    if coupon:
        order = Order.objects.filter(user=request.user, isordered=False).first()
        if order.getpayableamount() > coupon.amount:
          order.coupon = coupon
          order.save()
        else:
          messages.add_message(request,messages.ERROR,  message="this Coupon is not applicable in this Order Amount")
    else:
      messages.add_message(request, messages.ERROR, message="This coupon is invalid or Expired")
  return redirect(cart)             

        

def RemoveCoupon(request, coupon_id):
  coupon  = Coupon.objects.get(id=coupon_id)
  order = Order.objects.filter(user=request.user, isordered=False,from_buynow=False).last()
  if coupon:
    order.coupon = None
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
      orderitems = OrderItem.objects.filter(order=order.id)
      for item in orderitems:
        item.isordered =True
        item.save()
      
      order.save()
      return redirect("ordercomplete")
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET_KEY))
    payment = client.order.create({'amount': float(order.getpayableamount()*100) , 'currency': 'INR', 'payment_capture': 1})
    order.razor_pay_order_id = payment['id']
    order.save()

    razorpay_key = settings.RAZORPAY_KEY_ID
    return render(request, 'public/make-payment.html', {'payment':payment,'razorpay_key':razorpay_key})
  else:
    return redirect('address', id=order.id)
  
def completeorderitem(request,item,completeorder):
  complete_order_item = CompleteOrderItem()
  complete_order_item.product_title = item.variant_product.product.title
  complete_order_item.product_brand = item.variant_product.product.brand
  complete_order_item.product_discreption = item.variant_product.product.description
  complete_order_item.product_price = item.variant_product.price
  complete_order_item.product_discount_price = item.variant_product.dis_price

  # if item.variant_product.image:
  #   filename = os.path.basename(item.variant_product.image.name)  
  #   file_content = ContentFile(item.variant_product.image.read())
  #   complete_order_item.product_img.save(
  #       filename,
  #       file_content,
  #       save=False
  #   )
  # else:
  #   complete_order_item.product_img = None

  if item.variant_product.image and item.variant_product.image.storage.exists(item.variant_product.image.name):
    with item.variant_product.image.open('rb') as img_file:
        file_content = ContentFile(img_file.read())
        filename = os.path.basename(item.variant_product.image.name)
        complete_order_item.product_img.save(filename, file_content, save=False)
  else:
    complete_order_item.product_img = None


  complete_order_item.order = completeorder
  complete_order_item.qty = item.qty
  complete_order_item.save()

  return complete_order_item
    
def complete_order(request,order):
  completeorder = CompleteOrder()
  completeorder.user = request.user
  completeorder.price = order.gettotalamount()
  completeorder.discount = order.gettotaldiscount()
  completeorder.payable_amount = order.gettotaldiscountamount()
  if order.coupon:
    completeorder.coupon_code = order.coupon.code
    completeorder.coupon_amount = order.coupon.amount
  completeorder.razor_pay_order_id = order.razor_pay_order_id

  # address save
  completeorder.name = order.address.name
  completeorder.contact = order.address.contact
  completeorder.street = order.address.street
  completeorder.landmark = order.address.landmark
  completeorder.state = order.address.state
  completeorder.city = order.address.city
  completeorder.pincode = order.address.pincode
  completeorder.type = order.address.type
  completeorder.save()
 

  return completeorder

@login_required
def ordercomplete(request):

  order_id = request.GET.get('razorpay_order_id')
  

  order = Order.objects.get(razor_pay_order_id=order_id)
 
  order.isordered = True
  order.save()
  completeorder = complete_order(request,order)
  order_items = OrderItem.objects.filter(order = order)
  
  for item in order_items:
    item.isordered = True

    completeorderitem(request,item,completeorder)

    item.save()
   
    
  return redirect('success_payment')

#  temparary ordercomplete function for debug
# def ordercomplete(request):
#     order_id = request.GET.get('razorpay_order_id')
#     print("ORDER ID:", order_id)

#     try:
#         order = Order.objects.get(razor_pay_order_id=order_id)
#     except Exception as e:
#         print("ERROR WHILE FETCHING ORDER:", e)
#         return render(request, 'public/error_page.html', {"message": str(e)})

#     order.isordered = True
#     order.save()
#     return render(request, 'public/success_page.html', {"order": order})

def success_payment(request):
  return render(request, 'public/success_page.html')


@login_required
def my_order(request):

    orders = CompleteOrder.objects.filter(user=request.user)
  
    data = {
      "orders":orders,
    }
    return render(request, "public/my_order.html", data)

@login_required
def view_my_order(request,order_id):
  order = CompleteOrder.objects.get(user=request.user,id=order_id)
  return render(request,"public/view_order.html",{"order":order})