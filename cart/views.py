from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.contrib import messages

from django.core.exceptions import (
    ObjectDoesNotExist
)

from utils.decorators import (
    custom_login_required
)

from store.models import (
    Product,
    Variant
)

from .models import (
    Cart,
    CartItem
)


# =====================================
# ADD TO CART
# =====================================

@custom_login_required
def add_cart(request, product_id):

    product = get_object_or_404(

        Product,

        id=product_id,

        is_deleted=False,

        isBlocked=False,

        isActive=True
    )

    # =========================
    # GET VARIANT
    # =========================

    variant_id = request.POST.get(
        "variant_id"
    )

    variant = get_object_or_404(

        Variant,

        id=variant_id,

        product=product,

        is_active=True
    )

    # =========================
    # STOCK CHECK
    # =========================

    if variant.stock <= 0:

        messages.error(

            request,

            "Out of stock"
        )

        return redirect(
            "product_detail",
            slug=product.slug
        )

    # =========================
    # GET USER CART
    # =========================

    cart, created = Cart.objects.get_or_create(

        user=request.user
    )

    # =========================
    # CHECK EXISTING ITEM
    # =========================

    cart_item = CartItem.objects.filter(

        cart=cart,

        variant=variant

    ).first()

    # =========================
    # ITEM EXISTS
    # =========================

    if cart_item:

        # STOCK VALIDATION

        if cart_item.quantity >= variant.stock:

            messages.error(

                request,

                "Insufficient stock"
            )

            return redirect("cart")

        # MAX LIMIT

        if cart_item.quantity >= 5:

            messages.warning(

                request,

                "Maximum quantity limit reached"
            )

            return redirect("cart")

        cart_item.quantity += 1

        cart_item.save()

    # =========================
    # CREATE NEW ITEM
    # =========================

    else:

        CartItem.objects.create(

            cart=cart,

            product=product,

            variant=variant,

            quantity=1
        )

    messages.success(

        request,

        "Product added to cart"
    )

    return redirect("cart")


# =====================================
# CART PAGE
# =====================================

@custom_login_required
def cart(request):

    cart_items = []

    total = 0

    quantity = 0

    tax = 0

    grand_total = 0

    try:

        cart = Cart.objects.get(

            user=request.user
        )

        cart_items = CartItem.objects.filter(

            cart=cart

        ).select_related(

            "product",
            "variant"
        )

        # TOTALS

        for item in cart_items:

            item.total_price = (

                item.variant.salePrice *

                item.quantity
            )

            total += item.total_price

            quantity += item.quantity

        tax = (2 * total) / 100

        grand_total = total + tax

    except ObjectDoesNotExist:

        pass

    context = {

        "cart_items": cart_items,

        "total": total,

        "quantity": quantity,

        "tax": tax,

        "grand_total": grand_total,
    }

    return render(

        request,

        "store/cart.html",

        context
    )


# =====================================
# INCREASE QUANTITY
# =====================================

@custom_login_required
def increase_cart_quantity(request, cart_item_id):

    cart_item = get_object_or_404(

        CartItem,

        id=cart_item_id
    )

    # STOCK VALIDATION

    if cart_item.quantity >= cart_item.variant.stock:

        messages.error(

            request,

            "Insufficient stock"
        )

        return redirect("cart")

    # MAX LIMIT

    if cart_item.quantity >= 5:

        messages.warning(

            request,

            "Maximum quantity limit reached"
        )

        return redirect("cart")

    cart_item.quantity += 1

    cart_item.save()

    return redirect("cart")


# =====================================
# DECREASE QUANTITY
# =====================================

@custom_login_required
def decrease_cart_quantity(request, cart_item_id):

    cart_item = get_object_or_404(

        CartItem,

        id=cart_item_id
    )

    if cart_item.quantity > 1:

        cart_item.quantity -= 1

        cart_item.save()

    else:

        cart_item.delete()

    return redirect("cart")


# =====================================
# REMOVE ITEM
# =====================================

@custom_login_required
def remove_cart_item(request, cart_item_id):

    cart_item = get_object_or_404(

        CartItem,

        id=cart_item_id
    )

    cart_item.delete()

    messages.success(

        request,

        "Item removed from cart"
    )

    return redirect("cart")