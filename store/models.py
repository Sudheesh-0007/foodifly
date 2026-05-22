from django.db import models
from category.models import Category 
from cloudinary.models import CloudinaryField

class Product(models.Model):

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True) 
    description = models.TextField(blank=True)

    image = CloudinaryField('image', blank=True, null=True)

    averageRating = models.FloatField(default=0.0)
    reviewCount = models.IntegerField(default=0)
    isActive = models.BooleanField(default=True)
    isBlocked = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.name

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    variant_value= models.CharField(max_length=100, help_text="e.g., 500g, 1L, 250ml")
    stock = models.IntegerField(default=0)
    salePrice = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.weight}"
    
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE, related_name='gallery_images')
    image = CloudinaryField('image')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.product.name}"
    
    class Meta:
        verbose_name = 'productgallery'
        verbose_name_plural = 'product gallery'    