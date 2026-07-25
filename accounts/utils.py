from decimal import Decimal

from accounts.models import Referral
from wallet.models import Wallet, WalletTransaction

REFERRER_REWARD = Decimal("200")
REFERRED_REWARD = Decimal("100")


def process_referral_reward(order):
    print("========== REFERRAL FUNCTION CALLED ==========")

    user = order.user

    print("User:", user.email)
    print("Referred By:", user.referred_by)

    if not user.referred_by:
        print("User has no referrer")
        return

    try:
        referral = Referral.objects.get(referred_user=user)
        print("Referral record found")
    except Referral.DoesNotExist:
        print("Referral record NOT found")
        return

    print("Reward Given:", referral.reward_given)

    if referral.reward_given:
        print("Reward already given")
        return

    delivered_orders = user.order_set.filter(status="Delivered").count()
    print("Delivered Orders:", delivered_orders)

    if delivered_orders != 1:
        print("Not first delivered order")
        return

    print("Giving reward...")

    # Referrer wallet
    referrer_wallet, _ = Wallet.objects.get_or_create(user=user.referred_by)
    referrer_wallet.balance += REFERRER_REWARD
    referrer_wallet.save()

    WalletTransaction.objects.create(
        wallet=referrer_wallet,
        transaction_type="Credit",
        amount=REFERRER_REWARD,
        description=f"Referral reward for inviting {user.email}",
    )

    print("Referrer rewarded")

    # Referred user wallet
    referred_wallet, _ = Wallet.objects.get_or_create(user=user)
    referred_wallet.balance += REFERRED_REWARD
    referred_wallet.save()

    WalletTransaction.objects.create(
        wallet=referred_wallet,
        transaction_type="Credit",
        amount=REFERRED_REWARD,
        description="Welcome referral reward",
    )

    print("Referred user rewarded")

    referral.reward_given = True
    referral.save()

    print("Referral completed successfully")