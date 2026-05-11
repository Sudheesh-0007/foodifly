from django.db import models
from accounts.models import Account
from store.models import Product, Variant


class Wishlist(models.Model):

    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):

        return self.user.email


class WishlistItem(models.Model):

    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wishlist", "variant")

    def __str__(self):
        return f"{self.product.name}"
