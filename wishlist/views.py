from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from store.models import Product, Variant
from .models import Wishlist, WishlistItem
from utils.decorators import custom_login_required


@custom_login_required
def add_to_wishlist(request):

    if request.method == "POST":

        product_id = request.POST.get("product_id")

        if not product_id:

            messages.error(request, "Invalid product.")

            return redirect(request.META.get("HTTP_REFERER", "shop"))

        

        product = get_object_or_404(
            Product,
            id=product_id,
            is_deleted=False,
            isBlocked=False,
            isActive=True,
        )

    
        variant = Variant.objects.filter(product=product, is_active=True).first()

        if not variant:

            messages.error(request, "Variant unavailable.")

            return redirect(request.META.get("HTTP_REFERER", "shop"))

        

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
