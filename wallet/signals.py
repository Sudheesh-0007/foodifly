from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Account
from .models import Wallet


@receiver(post_save, sender=Account)
def create_wallet(sender, instance, created, **kwargs):

    if created:

        Wallet.objects.create(
            user=instance
        )
        print("WALLET CREATED FOR:", instance.email)