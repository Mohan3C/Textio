from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Size(models.Model):
    pass

class SizeVariant(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]
    size = models.CharField(max_length=3, choices=SIZE_CHOICES, unique=True)

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

    
    
