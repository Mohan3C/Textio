from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.

def home(request):
    return render(request,"main.html")


def registeruser(request):
  form = UserCreationForm(request.POST or None)

  if request.method == "POST":
    if form.is_valid():
      form.save()
      return redirect("login")  
  else:
    form = UserCreationForm()

  return render(request,"registration/registration.html",{"form":form})