from django.db import models
from django.contrib.auth.models import User

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.ForeignKey("Order", on_delete=models.CASCADE,blank=True,null=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(default=1)
    isordered = models.BooleanField(default=False)


    def __str__(self):
        return self.product_id.title
    

    def total_price(self):
        return self.product_id.price*self.qty
    
    def total_discount_price(self):
        return self.product_id.dis_price*self.qty
    
    def getpercentage(self):
        return(self.total_price()-self.total_discount_price())/self.total_price()*100

    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    isordered = models.BooleanField(default=False)
    address = models.ForeignKey("Address", on_delete=models.CASCADE, blank=True, null=True)
    coupon_id = models.ForeignKey("Coupon",on_delete=models.CASCADE, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    create_at =models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    def gettotalamount(self):
        total = 0
        for item in OrderItem.objects.filter(order_id=self.id):
            total += item.total_price()
        return total
    
    def gettotaldiscountamount(self):
        total_discount = 0
        for item in OrderItem.objects.filter(order_id=self.id):
            total_discount += item.total_discount_price()
        return total_discount
    
    def gettotaldiscount(self):
        return self.gettotalamount()-self.gettotaldiscountamount()

   
    def getpayableamount(self):
        if self.coupon_id:
            return self.gettotaldiscountamount() - self.coupon_id.amount 
        else:
            return self.gettotaldiscountamount() 

    def totalsaving(self):
        if self.coupon_id:
            return self.gettotaldiscount() + self.coupon_id.amount
        else:
            return self.gettotaldiscount()
    

    

class Coupon(models.Model):
    code = models.CharField(max_length=200)
    amount = models.FloatField(blank=False,null=False)

    def __str__(self):
        return self.code
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    alt_contact = models.CharField(max_length=100)
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