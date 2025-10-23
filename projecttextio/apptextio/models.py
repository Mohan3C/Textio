from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Size(models.Model):
    pass

class SizeVariant(models.Model):
    SIZE_CHOICES = [
        ( 'Small','S'),
        ( 'Medium','M'),
        ( 'Large','L'),
        ( 'Extra Large','XL'),
        
    ]
    size = models.CharField(max_length=12, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.get_size_display()

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="photo/")
    description = models.TextField()
    price = models.FloatField(default=0)
    dis_price = models.FloatField(default=None, blank=True, null=True)
    size = models.ManyToManyField(SizeVariant, related_name="products", blank=True)

    def __str__(self):
        sizes = ", ".join([size.get_size_display() for size in self.size.all()])
        return f"{self.title} - {sizes}"
    
class OrderItem(models.Model):
    temp_user = models.CharField(max_length=50,blank=True,null=True)
    order_id = models.ForeignKey("Order", on_delete=models.CASCADE,blank=True,null=True, related_name="items")
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    isordered = models.BooleanField(default=False)
    

    def __str__(self):
        if self.order_id.user:
            return str(self.order_id.id)
        else:
            return self.order_id.temp_user
    

    def total_price(self):
        total_price = Decimal(str(self.product_id.price*self.qty))
        return total_price
    
    def total_discount_price(self):
        total_discount_price = Decimal(str(self.product_id.dis_price*self.qty))
        return total_discount_price
    
    def getpercentage(self):
    
        return (self.total_price()-self.total_discount_price())/self.total_price()*100

    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,blank=True,null=True)
    temp_user = models.CharField(max_length=50,blank=True,null=True)
    isordered = models.BooleanField(default=False)
    address = models.ForeignKey("Address", on_delete=models.CASCADE, blank=True, null=True)
    coupon_id = models.ForeignKey("Coupon",on_delete=models.CASCADE, blank=True, null=True)
    create_at =models.DateTimeField(auto_now=True, blank=True, null=True)
    razor_pay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razor_pay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razor_pay_payment_signature = models.CharField(max_length=100, blank=True, null=True)
    from_buynow = models.BooleanField(default=False)
    


    def __str__(self):
        if self.user:
            return self.user.username
        return self.temp_user
    
    def gettotalamount(self):
        total = Decimal(0.00)
        item_total = 0
        for item in OrderItem.objects.filter(order_id=self.id):
            item_total += item.total_price()
            total = Decimal(str(item_total))
        return total
    
    def gettotaldiscountamount(self):
        total_discount = Decimal(0.00)
        item_discount = 0
        for item in OrderItem.objects.filter(order_id=self.id):
            item_discount += item.total_discount_price()
            total_discount = Decimal(str(item_discount))
        return total_discount
    
    def gettotaldiscount(self):
        gettotaldiscount = Decimal(str(self.gettotalamount()-self.gettotaldiscountamount()))
        return gettotaldiscount

   
    def getpayableamount(self):
        
        if self.coupon_id:
            getpayableamount = Decimal(str(self.gettotaldiscountamount() - self.coupon_id.amount))
            return  getpayableamount
        else:
            getpayableamount = Decimal(str(self.gettotaldiscountamount()))
            return  getpayableamount

    def totalsaving(self):
        if self.coupon_id:
            totalsaving = Decimal(str(self.gettotaldiscount() + self.coupon_id.amount))
            return totalsaving
        else:
            totalsaving = Decimal(str(self.gettotaldiscount()))
            return totalsaving

class CompleteOrderItem(models.Model):
    product_title = models.CharField(max_length=200)
    product_brand = models.CharField(max_length=50)
    product_price = models.DecimalField(max_digits=10,decimal_places=2)
    product_discount_price = models.DecimalField(max_digits=10,decimal_places=2)
    product_img = models.ImageField(upload_to="complete_order_item/")
    order = models.ForeignKey("CompleteOrder",on_delete=models.CASCADE,related_name="items")
    qty = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.product_title
    
class CompleteOrder(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    discount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    payable_amount = models.DecimalField(max_digits=10,decimal_places=2)
    coupon_code = models.CharField(max_length=50,blank=True,null=True)
    coupon_amount = models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    razor_pay_order_id = models.CharField(max_length=100)
    create_at = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    
    # address 
    name = models.CharField(max_length=200)
    contact = models.CharField(max_length=10)
    street = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    pincode = models.CharField(max_length=200)
    type = models.CharField(max_length=200)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=7,decimal_places=2)

    def __str__(self):
        return self.code
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    alt_contact = models.CharField(max_length=10)
    street = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200)
    city = models.CharField(max_length=200 , choices=(('Purnea','Purnea'),('Madhepura','Madhepura'),('Katihar','Katihar'),('Bhagelpur','Bhagelpur'),('Patna','Patna'),))
    state = models.CharField(max_length=200, choices=(('Bihar','Bihar'),('Up','Up'),('Jharkhand','Jharkhand'),('Punjab','Punjab'),('Haryana','Haryana'),))
    pincode = models.CharField(max_length=200)
    type = models.CharField(max_length=200, choices=(("Home","Home"),("Office","Office")))

    def __str__(self):
        return self.name
    
# class Payment(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     transication_id = models.CharField(max_length=200, blank=True, null=True)
#     create_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.transication_id