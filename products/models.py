from django.db import models
from django.utils import timezone
from django.db.models import Avg
from cloudinary.models import CloudinaryField

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Size(models.Model):
    SIZE_CHOICES = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
    ]
    name = models.CharField(max_length=5, choices=SIZE_CHOICES, unique=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    material = models.CharField(max_length=100)
    main_image = CloudinaryField('image', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
    
    @property
    def average_rating(self):
        average = self.reviews.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        return round(average, 1) if average else 0
    
    
class ProductSizeStock(models.Model):
    product = models.ForeignKey(Product, related_name='size_stock', on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField()

    class Meta:
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.product.name} - {self.size.name} ({self.stock})"
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='additional_images', on_delete=models.CASCADE)
    image = CloudinaryField('image')
    
    def __str__(self):
        return f"Imagen de {self.product.name}"
    
