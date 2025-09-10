from django.forms import ModelForm
from .models import *

class CategroyForm(ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

class ProductInsertForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        
class CouponcartForm(ModelForm):
    
    class Meta:
        model = Coupon
        fields = ["code"]

class CouponForm(ModelForm):

    class Meta:
        model = Coupon
        fields ="__all__"