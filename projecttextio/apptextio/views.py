from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import *

# Create your views here.

def home(request):
    products = Product.objects.all()
    return render(request,"public/main.html",{"products":products})

def viewproduct(request):
  products = Product.objects.all()
  return render(request, 'public/viewproduct.html',{'products':products})





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

def cart(request):
  return render(request,"public/cart.html")