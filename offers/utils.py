from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from offers.models import Offer


def get_offer_price(product, original_price):

    today = date.today()

    product_offer = Offer.objects.filter(
        offer_type="PRODUCT",
        product=product,
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
    ).first()

    category_offer = Offer.objects.filter(
        offer_type="CATEGORY",
        category=product.category,
        is_active=True,
        start_date__lte=today,
        end_date__gte=today,
    ).first()

    best_offer = None

    if product_offer and category_offer:

        if product_offer.discount_value > category_offer.discount_value:
            best_offer = product_offer
        else:
            best_offer = category_offer

    elif product_offer:

        best_offer = product_offer

    elif category_offer:

        best_offer = category_offer

    if not best_offer:
        return original_price, None

    if best_offer.discount_type == "PERCENTAGE":

        discounted_price = original_price - (
            original_price * best_offer.discount_value / Decimal("100")
        )

    else:

        discounted_price = original_price - best_offer.discount_value

    if discounted_price < 0:

        discounted_price = Decimal("0.00")

    discounted_price = discounted_price.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    return discounted_price, best_offer
