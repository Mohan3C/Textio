from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login

# Create your views here.

def home(request):
    return render(request,"public/main.html")

def viewproduct(request):
  return render(request, 'public/viewproduct.html')


def registeruser(request):

  if request.method == "POST":
    form = UserCreationForm(request.POST)

    if form.is_valid():
      user=form.save()
      login(request,user)
      messages.success(request,"Your account is created successfully")
      
      return redirect("homepage")  
    else:
      messages.error(request,"error")
  else:
    form = UserCreationForm()

  return render(request,"registration/register.html", {"form":form})