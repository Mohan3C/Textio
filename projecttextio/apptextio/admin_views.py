from django.shortcuts import render, redirect,get_object_or_404
from .admin_forms import CategroyForm, ProductInsertForm,CouponForm,VariantForm,VariantFormSet
from .models import *
from django.contrib.auth.decorators import login_required


def dashboard(request):
    if request.user.is_superuser:
        data = {}
        data['products'] = Product.objects.all()
        data['categories'] = Category.objects.all()
        data['coupons'] = Coupon.objects.all()
        data['users'] = User.objects.all()
        data['orders'] = Order.objects.all()
        return render(request,"admin/dashboard.html", data)
    else:
       return redirect("homepage")

def manageproduct(request):
    if request.user.is_superuser:
        products = Product.objects.prefetch_related('variants')
        return render(request,"admin/manage_products.html",{"products":products})
    else:
        return render(request,"public/main.html")
    

def view_variants(request,id):
    product = Product.objects.get(id = id)

    return render(request,"admin/view_variants.html",{"product":product})


def deleteProduct(request, id):
    itmes = Product.objects.get(id=id)
    itmes.delete()
    return redirect(manageproduct)

def insertProduct(request):
    productform = ProductInsertForm(request.POST or None)
    variantform = VariantFormSet(request.POST or None, request.FILES or None)
    if request.method == 'POST':
       if productform.is_valid() and variantform.is_valid():
          product = productform.save()
          variants = variantform.save(commit=False)
          for variant in variants:
              variant.product = product
              variant.save()
          return redirect(manageproduct)

    return render(request, 'admin/insert_product.html', {'productform':productform,"variantform":variantform})

def edit_product(request,id):
    product = get_object_or_404(Product,id=id)
    
    edit_productform = ProductInsertForm(request.POST or None,instance=product)
    if request.method == "POST":
        if edit_productform.is_valid():
            edit_productform.save()
        return redirect("manageproduct")
    
    return render(request,"admin/insert_product.html",{"edit_productform":edit_productform,"product":product})


def add_variant(request,id):
    product = get_object_or_404(Product,id=id)
    
    variantform = VariantFormSet(request.POST or None , request.FILES or None)
    if request.method == "POST":
        if variantform.is_valid():
            variants = variantform.save(commit=False)

            for variant in variants:
                variant.product = product
                variant.save()
            return redirect("viewvariants")
    
    return render(request,"admin/addvariant.html",{"variantform":variantform,"product":product})

def edit_variant(request,id):
    variant = get_object_or_404(Variant,id=id)

    var_form = VariantForm(request.POST or None, request.FILES or None,instance=variant)
    if request.method == "POST":
        if var_form.is_valid():
            var_form.save()
        return redirect("viewvariants")
    
    return render(request,"admin/addvariant.html",{"var_form":var_form,"variant":variant})

def delete_variant(request,id):
    variant = Variant.objects.get(id=id)
    variant.delete()
    return redirect('viewvariants')


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

def deleteuser(request,id):
    user = User.objects.get(id=id)
    user.delete()
    return redirect(manageUser)

def manageOrder(request):
    data = {}
    data["orders"] = Order.objects.all()
    return render(request, 'admin/manage_order.html', data)

def managePayment(request):
    data = {}
    data['orders'] = Order.objects.filter(user=request.user , isordered = True)
    return render(request, 'admin/manage_payment.html', data)

