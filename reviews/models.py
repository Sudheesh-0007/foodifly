from django.db import models

from accounts.models import Account
from store.models import Product


class Review(models.Model):

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE)

    rating = models.PositiveIntegerField()

    review = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "user")

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
