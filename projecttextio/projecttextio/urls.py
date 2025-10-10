
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apptextio.views import *
from apptextio.admin_views import *

urlpatterns = [
    path('superadmin/', admin.site.urls),
    path("", home, name="homepage"),
    path("viewproduct/<int:id>/", viewproduct, name="viewproduct"),
    path("allproducts/",products,name="products"),
    path("allproducts/<int:id>/",products,name="filter"),
    path("address/<int:id>/",checkoutaddress ,name="address"),
    path("address-info/",addAddressInfo ,name="address-info"),
    path("buynow/<int:id>/",buynow ,name="buynow"),
    path("success-page/",success ,name="success"),

    # cart and coupon urls
    path("home/product/cart",cart,name="cart"),
    path("order/<int:product_id>/add-to-cart/",addtocart,name="addtocart"),
    path("order/<int:product_id>/remove-from-cart/",removefromcart,name="removefromcart"),
    path("order/<int:product_id>/delete-from-cart/",deletefromcart,name="deletefromcart"),
    path("my-order/complete/",my_order,name="my_order"),
    path("addCoupon/", addCoupon, name="addCoupon"),
    path("Couponadd/<int:id>/", buynowaddCoupon, name="buynowaddCoupon"),
    path("removecouponfrombuynow/<int:coupon_id>/", removecouponfrombuynow, name="removecouponfrombuynow"),
    path("makepayment/", payment, name="makepayment"),
    path("RemoveCoupon/<int:coupon_id>/", RemoveCoupon, name="RemoveCoupon"),
    path("admin/coupons", manageCoupons, name="manageCoupons"),
    path("admin/coupons/<int:id>/delete/", delete_coupon, name="deletecoupon"),


    # default login urls
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/registration/",registeruser, name="registration"),
       
       
        # admin urls
    path("admin-base/",dashboard,name="dashboard"),
    path("manage-category/",managecategory,name="managecategory"),
    path("manage-product/",manageproduct,name="manageproduct"),
    path("manage-address/",saveAddress,name="manageaddress"),
    path("manage-user/",manageUser,name="manageuser"),
    path("manage-user/delete/<int:id>/",deleteuser,name="deleteuser"),
    path("manage-order/",manageOrder,name="manageorder"),
    path("manage-payment/",managePayment,name="managepayment"),
    path("delete-product/<int:id>/",deleteProduct ,name="deleteproduct"),
    path("insert-product/",insertProduct,name="insert-product"),
    path("delete-product/<int:id>/",deleteCategory ,name="delete-product"),


]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)