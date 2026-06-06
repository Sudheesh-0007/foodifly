from django.db import models

# Create your models here.
from django.db import models
from accounts.models import Account


class Wallet(models.Model):

    user = models.OneToOneField(
        Account, on_delete=models.CASCADE, related_name="wallet"
    )

    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} Wallet"


class WalletTransaction(models.Model):

    TRANSACTION_TYPES = (
        ("Credit", "Credit"),
        ("Debit", "Debit"),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - ₹{self.amount}"
