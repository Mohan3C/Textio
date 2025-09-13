# admin.py
from django.contrib import admin
from .models import *

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price', 'get_sizes')

    def get_sizes(self, obj):
        return ", ".join([s.get_size_display() for s in obj.size.all()])

    get_sizes.short_description = "Sizes"

admin.site.register(Product, ProductAdmin)
admin.site.register(SizeVariant)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Coupon)
admin.site.register(Address)
