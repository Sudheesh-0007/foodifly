from django.db import models

from accounts.models import Account

from store.models import Product, Variant


class Cart(models.Model):

    user = models.OneToOneField(Account, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return self.user.email


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        unique_together = ("cart", "variant")

    def __str__(self):

        return f"{self.product.product_name}"
