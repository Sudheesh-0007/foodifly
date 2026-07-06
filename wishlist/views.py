from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from offers.utils import get_offer_price
from store.models import Product, Variant
from utils.decorators import custom_login_required

from .models import Wishlist, WishlistItem


@custom_login_required
def add_to_wishlist(request):

    if request.method == "POST":

        product_id = request.POST.get("product_id")

        variant_id = request.POST.get("variant_id")

        if not product_id:

            messages.error(request, "Invalid product.")

            return redirect(request.META.get("HTTP_REFERER", "shop"))

        product = get_object_or_404(
            Product,
            id=product_id,
            is_deleted=False,
            isBlocked=False,
        )
        if not product.isActive:

            messages.warning(request, "This product is currently unavailable.")

            return redirect("product_detail", slug=product.slug)

        if not variant_id:

            messages.error(request, "Please select a variant.")

            return redirect(request.META.get("HTTP_REFERER", "shop"))

        variant = get_object_or_404(
            Variant, id=variant_id, product=product, is_active=True
        )

        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

        exists = WishlistItem.objects.filter(
            wishlist=wishlist, variant=variant
        ).exists()

        if exists:

            messages.warning(request, "Already in wishlist.")

            return redirect(request.META.get("HTTP_REFERER", "shop"))

        WishlistItem.objects.create(wishlist=wishlist, product=product, variant=variant)

        messages.success(request, "Added to wishlist.")

        return redirect(request.META.get("HTTP_REFERER", "shop"))

    return redirect("shop")


@custom_login_required
def wishlist_page(request):

    wishlist_items = (
        WishlistItem.objects.filter(wishlist__user=request.user)
        .select_related("product", "variant", "product__category")
        .order_by("-id")
    )
    for item in wishlist_items:

        offer_price, offer = get_offer_price(item.product, item.variant.salePrice)

        item.offer_price = offer_price
        item.offer = offer
    paginator = Paginator(wishlist_items, 5)

    page = request.GET.get("page")

    paginated_items = paginator.get_page(page)

    context = {"wishlist_items": paginated_items}

    return render(request, "store/wishlist.html", context)


@custom_login_required
def remove_wishlist_item(request, item_id):

    wishlist_item = get_object_or_404(
        WishlistItem, id=item_id, wishlist__user=request.user
    )
    wishlist_item.delete()

    messages.success(request, "Item removed from wishlist")
    return redirect("wishlist_page")
