
from django.contrib import admin
from django.urls import path, include

from apptextio.views import *

urlpatterns = [
    path('superadmin/', admin.site.urls),
    path("", home, name="homepage"),
    path("viewproduct/", viewproduct, name="allproduct"),


    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/registration/",registeruser, name="registration"),

    path("admin/admin-base/",dashboard,name="dashboard"),
    path("admin/managecategory/",managecategory,name="managecategory"),
    path("admin/manageproduct/",manageproduct,name="manageproduct"),


]
