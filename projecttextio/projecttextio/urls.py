
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apptextio.views import *
from apptextio.admin_views import *

urlpatterns = [
    path('superadmin/', admin.site.urls),
    path("", home, name="homepage"),
    path("viewproduct/", viewproduct, name="allproduct"),
    path("home/product/cart",cart,name="cart"),


    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/registration/",registeruser, name="registration"),
        # admin urls
    path("admin/admin-base/",dashboard,name="dashboard"),
    path("manage-category/",managecategory,name="managecategory"),
    path("manage-product/",manageproduct,name="manageproduct"),
    path("delete-product/<int:id>/",deleteProduct ,name="deleteproduct"),
    path("insert-product/",insertProduct,name="insert-product"),
    path("delete-product/<int:id>/",deleteCategory ,name="delete-product"),


]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)