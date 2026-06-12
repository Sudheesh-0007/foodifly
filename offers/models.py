from django.db import models

# Create your models here.
from django.db import models
from category.models import Category
from store.models import Product


class Offer(models.Model):

    OFFER_TYPES = (
        ("PRODUCT", "Product"),
        ("CATEGORY", "Category"),
    )

    DISCOUNT_TYPES = (
        ("PERCENTAGE", "Percentage"),
        ("FIXED", "Fixed Amount"),
    )

    name = models.CharField(max_length=100)

    offer_type = models.CharField(max_length=20, choices=OFFER_TYPES)

    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)

    discount_value = models.DecimalField(max_digits=10, decimal_places=2)

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, null=True, blank=True
    )

    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, null=True, blank=True
    )

    start_date = models.DateField()

    end_date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
