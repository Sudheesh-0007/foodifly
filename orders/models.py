from django.db import models
from accounts.models import Account, Address
from store.models import Product, Variant


class Order(models.Model):

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
    )

    PAYMENT_METHODS = (
        ("COD", "Cash On Delivery"),
        ("RAZORPAY", "Razorpay"),
        ("WALLET", "Wallet"),
    )

    PAYMENT_STATUS_CHOICES = (
    ("Pending", "Pending"),
    ("Paid", "Paid"),
    ("Failed", "Failed"),
    ("Refunded", "Refunded"),
)

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    order_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    payment_status = models.CharField(max_length=20,choices=PAYMENT_STATUS_CHOICES,default="Pending")

    razorpay_order_id = models.CharField(max_length=200,blank=True,null=True)
    razorpay_payment_id = models.CharField(max_length=200,blank=True,null=True)


    def __str__(self):
        return self.order_number


class OrderItem(models.Model):

    ITEM_STATUS = (
        ("Active", "Active"),
        ("Cancelled", "Cancelled"),
        ("Returned", "Returned"),
    )
    RETURN_STATUS = (
        ("Not Requested", "Not Requested"),
        ("Requested", "Requested"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ITEM_STATUS, default="Active")

    return_requested = models.BooleanField(default=False)
    return_reason = models.TextField(blank=True, null=True)
    return_status = models.CharField(max_length=20, choices=RETURN_STATUS, default="Not Requested" )

    def __str__(self):

        return self.product.name
