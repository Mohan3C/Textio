# admin.py
from django.contrib import admin
from .models import *

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'get_variants')
    inlines = [VariantInline]

    def get_variants(self, obj):
        return ", ".join([f"{v.color} - {v.size.get_size_display()}" for v in obj.variants.all()])
    get_variants.short_description = "Variants"


admin.site.register(Product, ProductAdmin)
admin.site.register(SizeVariant)
admin.site.register(Variant)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Address)
admin.site.register(CompleteOrder)
admin.site.register(CompleteOrderItem)
