from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from utils.decorators import custom_login_required
from store.models import Product, Variant
from .models import Cart, CartItem
from wishlist.models import WishlistItem


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
            cart=cart,
            product__is_deleted=False,
            product__isBlocked=False,
            product__isActive=True,
        ).select_related("product", "variant")

        for item in cart_items:
           
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

                    f"{item.product.name} quantity adjusted to available stock."
                )

                messages.warning(
                    request,
                    f"Only {item.variant.stock} quantity available for {item.product.name}.",
                )
            else:

                item.stock_issue = False

            item.total_price = item.variant.salePrice * item.quantity

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

    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if cart_item.quantity >= cart_item.variant.stock:
        messages.error(request, "Insufficient stock")
        return redirect("cart")

    if cart_item.quantity >= 5:
        messages.warning(request, "Maximum quantity limit reached")
        return redirect("cart")

    cart_item.quantity += 1
    cart_item.save()
    return redirect("cart")


@custom_login_required
def decrease_cart_quantity(request, cart_item_id):

    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if cart_item.quantity > 1:

        cart_item.quantity -= 1

        cart_item.save()

    else:

        cart_item.delete()

    return redirect("cart")


@custom_login_required
def remove_cart_item(request, cart_item_id):

    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    cart_item.delete()

    messages.success(request, "Item removed from cart")

    return redirect("cart")
