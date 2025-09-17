from django.shortcuts import render, redirect,get_object_or_404
from .admin_forms import CategroyForm, ProductInsertForm,CouponForm
from .models import *
from django.contrib.auth.decorators import login_required


def dashboard(request):
  data = {}
  data['products'] = Product.objects.all()
  data['categories'] = Category.objects.all()
  data['coupons'] = Coupon.objects.all()
  data['users'] = User.objects.all()
  return render(request,"admin/dashboard.html", data)

def manageproduct(request):
  products = Product.objects.all()
  return render(request,"admin/manage_products.html",{"products":products})



def deleteProduct(request, id):
    itmes = Product.objects.get(id=id)
    itmes.delete()
    return redirect(manageproduct)

def insertProduct(request):
    form = ProductInsertForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
       if form.is_valid():
          form.save()
          return redirect(manageproduct)

    return render(request, 'admin/insert_product.html', {'form':form})

def managecategory(request):
    form = CategroyForm(request.POST or None)
    categories = Category.objects.all()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(managecategory)
    return render(request,"admin/manage_category.html", {'categories':categories ,'form':form})

def deleteCategory(request, id):
   item = Category.objects.get(id=id)
   item.delete()
   return redirect(managecategory)



def manageCoupons(req):
    coupon_form = CouponForm(req.POST or None)
    coupons = Coupon.objects.all()
    
    if req.method == "POST":
        if coupon_form.is_valid():
            coupon_form.save()
            return redirect(manageCoupons)
    return render(req, "admin/manage_coupon.html", {"coupons":coupons, "form":coupon_form})



def delete_coupon(request,id):
    data = get_object_or_404(Coupon,id=id)

    data.delete()
    return redirect("manageCoupons")

def saveAddress(request):
    addresses  = Address.objects.filter(user = request.user)
    return render(request, 'admin/manage_address.html', {'addresses':addresses})

def manageUser(request):
    data = {}
    data['users'] = User.objects.all()
    return render(request, 'admin/users.html', data)

def manageOrder(request):
    data = {}
    data["orders"] = Order.objects.all()
    return render(request, 'admin/manage_order.html', data)