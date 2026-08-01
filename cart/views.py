from decimal import Decimal

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from offers.utils import get_offer_price
from store.models import Product, Variant
from utils.decorators import custom_login_required
from wishlist.models import WishlistItem

from .models import Cart, CartItem


@custom_login_required
def add_cart(request, product_id):

    product = get_object_or_404(
        Product, id=product_id, is_deleted=False, isBlocked=False, isActive=True
    )

    variant_id = request.POST.get("variant_id")
    if not variant_id:
        messages.error(request, "Please select a variant")
        return redirect("product_detail", slug=product.slug)

    variant = get_object_or_404(Variant, id=variant_id, product=product, is_active=True)

    if variant.stock <= 0:
        messages.error(request, "Out of stock")
        return redirect("product_detail", slug=product.slug)

    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item = CartItem.objects.filter(cart=cart, variant=variant).first()

    if not product.category.is_active or product.category.is_deleted:

        messages.error(request, "This product category is currently unavailable.")

        return redirect("product_detail", slug=product.slug)
    if cart_item:
        if cart_item.quantity >= variant.stock:
            messages.error(request, "Insufficient stock")
            return redirect("cart")

        if cart_item.quantity >= 5:
            messages.warning(request, "Maximum quantity limit reached")
            return redirect("cart")

        cart_item.quantity += 1
        cart_item.save()

    else:

        CartItem.objects.create(cart=cart, product=product, variant=variant, quantity=1)

    WishlistItem.objects.filter(wishlist__user=request.user, variant=variant).delete()
    messages.success(request, "Product added to cart")
    return redirect("cart")


@custom_login_required
def cart(request):

    cart_items = []
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    can_checkout = True

    try:

        cart = Cart.objects.get(user=request.user)

        cart_items = CartItem.objects.filter(
            cart=cart
        ).select_related("product", "variant", "product__category")

        for item in cart_items:
            if (
                not item.product.isActive
                or item.product.is_deleted
                or not item.product.category.is_active
                or item.product.category.is_deleted
            ):

                item.stock_issue = False
                item.unavailable = True

                can_checkout = False

                messages.warning(
                    request, f"{item.product.name} is currently unavailable."
                )

                continue

            item.unavailable = False

            if item.variant.stock <= 0:

                item.stock_issue = True

                can_checkout = False

                messages.warning(request, f"{item.product.name} is out of stock.")

            elif item.quantity > item.variant.stock:

                item.quantity = item.variant.stock

                item.save()

                item.stock_issue = True

                messages.warning(
                    request,
                    f"{item.product.name} quantity adjusted to available stock.",
                )

                messages.warning(
                    request,
                    f"Only {item.variant.stock} quantity available for {item.product.name}.",
                )
            else:

                item.stock_issue = False
            offer_price, offer = get_offer_price(item.product, item.variant.salePrice)

            item.offer_price = offer_price
            item.offer = offer

            item.total_price = offer_price * item.quantity

            total += item.total_price

            quantity += item.quantity

        tax = total / 10

        grand_total = total + tax

    except ObjectDoesNotExist:

        pass

    context = {
        "cart_items": cart_items,
        "total": total,
        "quantity": quantity,
        "tax": tax,
        "grand_total": grand_total,
        "can_checkout": can_checkout,
    }

    return render(request, "store/cart.html", context)


@custom_login_required
def increase_cart_quantity(request, cart_item_id):

    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    if cart_item.quantity >= cart_item.variant.stock:
        return JsonResponse({"success": False, "message": "Insufficient stock"})

    if cart_item.quantity >= 5:
        return JsonResponse(
            {"success": False, "message": "Maximum quantity limit reached"}
        )

    cart_item.quantity += 1
    cart_item.save()

    cart = cart_item.cart

    total = Decimal("0")
    quantity = 0

    for item in CartItem.objects.filter(cart=cart):

        offer_price, _ = get_offer_price(item.product, item.variant.salePrice)

        total += offer_price * item.quantity
        quantity += item.quantity

    tax = total / Decimal("10")
    grand_total = total + tax

    offer_price, _ = get_offer_price(cart_item.product, cart_item.variant.salePrice)

    return JsonResponse(
        {
            "success": True,
            "quantity": cart_item.quantity,
            "item_total": float(offer_price * cart_item.quantity),
            "subtotal": float(total),
            "tax": float(tax),
            "grand_total": float(grand_total),
            "cart_items": quantity,
        }
    )


@custom_login_required
def decrease_cart_quantity(request, cart_item_id):

    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    if cart_item.quantity > 1:

        cart_item.quantity -= 1
        cart_item.save()

    else:

        cart_item.delete()
        return JsonResponse({"success": True, "deleted": True})

    cart = cart_item.cart

    total = Decimal("0")
    quantity = 0

    for item in CartItem.objects.filter(cart=cart):

        offer_price, _ = get_offer_price(item.product, item.variant.salePrice)

        total += offer_price * item.quantity
        quantity += item.quantity

    tax = total / Decimal("10")
    grand_total = total + tax

    offer_price, _ = get_offer_price(cart_item.product, cart_item.variant.salePrice)

    return JsonResponse(
        {
            "success": True,
            "deleted": False,
            "quantity": cart_item.quantity,
            "item_total": float(offer_price * cart_item.quantity),
            "subtotal": float(total),
            "tax": float(tax),
            "grand_total": float(grand_total),
            "cart_items": quantity,
        }
    )


@custom_login_required
def remove_cart_item(request, cart_item_id):

    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)

    cart = cart_item.cart

    cart_item.delete()

    total = Decimal("0")
    quantity = 0

    for item in CartItem.objects.filter(cart=cart):

        offer_price, _ = get_offer_price(item.product, item.variant.salePrice)

        total += offer_price * item.quantity
        quantity += item.quantity

    tax = total / Decimal("10")
    grand_total = total + tax

    return JsonResponse(
        {
            "success": True,
            "subtotal": float(total),
            "tax": float(tax),
            "grand_total": float(grand_total),
            "cart_items": quantity,
        }
    )
