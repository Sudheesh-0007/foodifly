from django.db.models import Min, Q
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from offers.utils import get_offer_price
from store.models import Product


def home(request):

    latest_products = (
        Product.objects.filter(
            is_deleted=False, isBlocked=False, isActive=True, variants__is_active=True
        )
        .annotate(
            starting_price=Min(
                "variants__salePrice", filter=Q(variants__is_active=True)
            )
        )
        .distinct()
        .order_by("-createdAt")[:4]
    )
    for product in latest_products:

        cheapest_variant = (
            product.variants.filter(is_active=True).order_by("salePrice").first()
        )

        if cheapest_variant:

            offer_price, offer = get_offer_price(product, cheapest_variant.salePrice)

            product.original_price = cheapest_variant.salePrice
            product.offer_price = offer_price
            product.offer = offer

    featured_product = (
        Product.objects.filter(
            is_deleted=False, isBlocked=False, isActive=True, variants__is_active=True
        )
        .annotate(starting_price=Min("variants__salePrice"))
        .distinct()
        .last()
    )
    from reviews.models import Review

    featured_reviews = (
        Review.objects.filter(is_active=True, rating=5)
        .select_related("user", "product")
        .order_by("-created_at")[:3]
    )

    if featured_reviews.count() < 3:
        featured_reviews = (
            Review.objects.filter(is_active=True)
            .select_related("user", "product")
            .order_by("-rating", "-created_at")[:3]
        )

    context = {
        "latest_products": latest_products,
        "featured_product": featured_product,
        "context_reviews": featured_reviews,
    }

    return render(request, "home.html", context)
