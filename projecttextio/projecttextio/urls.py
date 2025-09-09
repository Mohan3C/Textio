
from django.contrib import admin
from django.urls import path,include

from apptextio.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("",home,name="homepage"),


    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/registration/",registeruser,name="registration"),

]
