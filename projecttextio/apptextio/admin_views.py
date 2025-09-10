from django.shortcuts import render, redirect
from .admin_forms import CategroyForm, ProductInsertForm
from .models import *


def dashboard(request):
  return render(request,"admin/dashboard.html")

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


