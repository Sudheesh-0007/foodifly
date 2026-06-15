from django.db import models



class Coupon(models.Model):

    code = models.CharField(max_length=50, unique=True)

    discount_type = models.CharField(
        max_length=20,
        choices=(
            ("PERCENTAGE", "Percentage"),
            ("FIXED", "Fixed Amount"),
        ),
    )

    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    valid_from = models.DateField()
    valid_to = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code
