from django.forms import ModelForm,inlineformset_factory
from .models import *

class CategroyForm(ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

class ProductInsertForm(ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

class VariantForm(ModelForm):

    class Meta:
        model = Variant
        fields = "__all__"

VariantFormSet = inlineformset_factory(Product,Variant,form=VariantForm,extra=1)
        
class CouponcartForm(ModelForm):
    
    class Meta:
        model = Coupon
        fields = ["code"]

class CouponForm(ModelForm):

    class Meta:
        model = Coupon
        fields ="__all__"

class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ['name','contact','street','landmark','city','state','pincode','type']